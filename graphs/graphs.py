import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def importbases():

    try:
        signals = pd.read_json(r'statistics\DIJSignals.json')
        dij_reduce = pd.read_json(r'database\DIJ_ETL.json')

    except Exception as e:
        print(f'Error loading databases: {e}')
        raise

    return signals, dij_reduce


def plot_dij_signals(symbol: str):
    signals, _ = importbases()

    symbol = symbol.strip().upper()
    filtered = signals.loc[signals['Symbol'] == symbol].copy()

    if filtered.empty:
        print(f'No signals found for {symbol}.')
        return filtered

    filtered['Date'] = pd.to_datetime(filtered['Date'])
    filtered = filtered.sort_values('Date')

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(filtered['Date'], filtered['Sum_Signals'], marker='o')
    ax.set_title(f'{symbol} — Signal History')
    ax.set_xlabel('Date')
    ax.set_ylabel('Sum of Signals')
    ax.grid(alpha=0.3)

    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))

    fig.autofmt_xdate()
    fig.tight_layout()

    fig.savefig(f'{symbol}_signals.png', dpi=300, bbox_inches='tight')
    plt.show()

    return filtered

plot_dij_signals("DI1F27")