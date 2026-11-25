import sys
import os
import json
import torch
import pandas as pd

from pairDIJ.findP import metrics_pairs

dv01 = 5000
std_in = 0.30
std_out = 0.15

def save_backtest_to_json(backtest_results: list, filename: str = "backtest_results.json"):
    """
    Saves the compiled backtest results inside the project's 'database' folder.
    """
    
    db_folder = os.path.join(os.getcwd(), "database")
    os.makedirs(db_folder, exist_ok=True)
    
    file_path = os.path.join(db_folder, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(backtest_results, f, indent=4)
        
    print(f"[SUCCESS] Backtest metrics successfully exported to: {file_path}")

def run_spread_backtest_pytorch():
    
    data = pd.read_json(r'database\DIJ_ETL.json')
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.sort_values(['Symbol', 'Date'])

    dates_sorted = sorted(data['Date'].dropna().unique())

    start_date_input = input(
        "Enter the backtest start date (YYYY-MM-DD), or press Enter to use the first available date: "
    ).strip()

    if start_date_input:
        requested_start_date = pd.to_datetime(start_date_input)
        available_dates = [date for date in dates_sorted if date >= requested_start_date]

        if not available_dates:
            raise ValueError(
                "There are no available data dates on or after the selected date."
            )

        start_date = available_dates[0]
    else:
        start_date = dates_sorted[0]

    metrics = metrics_pairs()

    active_pairs = metrics[(metrics['signal'] != 'No signal')].copy()

    results = []

    for _, pair in active_pairs.iterrows():

        symbol_A, symbol_B = pair['Pairs'].split(' x ')
        direction = 1 if pair['signal'] == 'Long spread' else -1

        pair_data = data[data['Symbol'].isin([symbol_A, symbol_B]) & (data['Date'] >= start_date)]

        prices = pair_data.pivot(
            index='Date',
            columns='Symbol',
            values='Avg_Price'
        ).dropna(subset=[symbol_A, symbol_B])

        spread = (prices[symbol_A] - prices[symbol_B]) * 100
        daily_change = spread.diff().dropna()

        if daily_change.empty:
            continue

        daily_changes_tensor = torch.tensor(
            daily_change.to_numpy(),
            dtype=torch.float32
        )

        daily_std = torch.std(daily_changes_tensor, unbiased=True)

        if torch.isnan(daily_std) or daily_std.item() == 0:
            continue

        stop_limit = round(0.15 * daily_std.item() * 5000, 4)
        profit_limit = round(0.30 * daily_std.item() * 5000, 4)
        cumulative_pnl = 0

        for date, change in daily_change.items():

            daily_pnl = round(direction * 5000 * change, 2)
            cumulative_pnl += daily_pnl

            exit_reason = None

            if cumulative_pnl <= -stop_limit:
                exit_reason = 'Stop loss'
            elif cumulative_pnl >= profit_limit:
                exit_reason = 'Take profit'

            results.append({
                'Date': date,
                'Pairs': pair['Pairs'],
                'signal': pair['signal'],
                'spread_change_bps': change,
                'daily_pnl': daily_pnl,
                'cumulative_pnl': cumulative_pnl,
                'stop_limit': stop_limit,
                'profit_limit': profit_limit,
                'exit_reason': exit_reason
            })

            if exit_reason is not None:
                break

    backtest_results = pd.DataFrame(results)

    results_to_save = backtest_results.to_dict(orient='records')

    for row in results_to_save:
        if pd.notna(row.get('Date')):
            row['Date'] = row['Date'].isoformat()

    save_backtest_to_json(results_to_save)

    return backtest_results

def top_5_by_operation(
    filename=r'database\backtest_results.json'
):

    with open(filename, 'r', encoding='utf-8') as f:
        backtest_results = json.load(f)

    df = pd.DataFrame(backtest_results)

    if df.empty:
        print("No backtest results found.")
        return

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    final_results = df.groupby(
        ['Pairs', 'signal'],
        as_index=False
    ).tail(1)

    for signal, operation in [
        ('Short spread', 'Short'),
        ('Long spread', 'Long')
    ]:
        top_5 = final_results[
            final_results['signal'] == signal
        ].nlargest(5, 'cumulative_pnl')

        print(f'\n{operation} — Top 5')

        if top_5.empty:
            print("No results found.")
            continue

        print(
            top_5[
                ['Pairs', 'cumulative_pnl', 'spread_change_bps']
            ].rename(columns={
                'Pairs': 'Pair',
                'cumulative_pnl': 'PnL',
                'spread_change_bps': 'Spread change (bps)'
            }).to_string(index=False)
        )
