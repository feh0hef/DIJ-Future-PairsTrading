import pandas as pd
import numpy as np
import json
from tools.calculate_fuctions import Spread_DIJ

def historical_pairs():

    with open(r'database\daily_covariance.json', 'r', encoding='utf-8') as f:
        cov = json.load(f)

    flattened_pairs = []

    for cluster_key, pairs in cov.items():
        for pair in pairs:
            flattened_pairs.append({
                "cluster_pair": cluster_key,
                "symbol_A": pair["symbol_A"],
                "symbol_B": pair["symbol_B"]
            })

    data = pd.read_json(r'database\DIJ_ETL.json')
    data['Date'] = pd.to_datetime(data['Date'])

    dates_sorted = sorted(data['Date'].dropna().unique())
    historical_spreads = []

    use_default_date = input(
        "Do you want to use the default date range to find pairs? (y/n): "
    ).lower()

    if use_default_date == 'y':
        start_index = 0
    else:
        initial_date = pd.to_datetime(
            input("Enter the initial date (YYYY-MM-DD): ")
        )

        if initial_date not in dates_sorted:
            raise ValueError("The selected date is not present in the database.")

        start_index = dates_sorted.index(initial_date)

    for i in range(start_index, len(dates_sorted) - 7):

        day_0 = dates_sorted[i]
        day_1w = dates_sorted[i + 7]

        spread_values = Spread_DIJ(data, flattened_pairs, day_0, day_1w)

        for spread in spread_values:
            historical_spreads.append({
                "Date": day_0,
                "Date_1w": day_1w,
                "Pairs": spread["symbol_A"] + " x " + spread["symbol_B"],
                "spread_day0_bps": spread["spread_day0_bps"],
                "spread_last_day_bps": spread["spread_last_day_bps"],
                "spread_change_bps": spread["spread_change_bps"]
            })

    return historical_spreads  


def metrics_pairs():

    historical_spreads = historical_pairs()
    df = pd.DataFrame(historical_spreads)

    metrics = df.groupby('Pairs').agg(
        mean_spread_change_bps=('spread_change_bps', 'mean'),
        std_spread_change_bps=('spread_change_bps', 'std'),
        max_spread_change_bps=('spread_change_bps', 'max'),
        min_spread_change_bps=('spread_change_bps', 'min'),
        last_spread_change_bps=('spread_change_bps', 'last')
    ).reset_index()

    metrics = metrics[metrics['std_spread_change_bps'] > 3].copy()

    metrics['distance_to_max_bps'] = (
        metrics['max_spread_change_bps'] - metrics['last_spread_change_bps']
    )

    metrics['distance_to_min_bps'] = (
        metrics['last_spread_change_bps'] - metrics['min_spread_change_bps']
    )


    metrics['distance_to_max_std'] = (
        metrics['distance_to_max_bps'] / metrics['std_spread_change_bps']
    )

    metrics['distance_to_min_std'] = (
        metrics['distance_to_min_bps'] / metrics['std_spread_change_bps']
    )

    metrics['signal'] = 'No signal'

    metrics.loc[
        metrics['distance_to_max_std'] <= 5,
        'signal'
    ] = 'Long spread'

    metrics.loc[
        metrics['distance_to_min_std'] <= 5,
        'signal'
    ] = 'Short spread'

    return metrics.sort_values(
        by='std_spread_change_bps',
        ascending=False
    )