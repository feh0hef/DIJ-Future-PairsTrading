import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch
from sklearn.decomposition import PCA
from statistics.cov import signal_correlation, cluster_signal_correlation
import pandas as pd
import numpy as np

def importbases():

    try:
        signals = pd.read_json(r'database\DIJSignals.json')
        dij_reduce = pd.read_json(r'database\DIJ_ETL.json')
        backtest = pd.read_json(r'database\backtest_results.json')

    except Exception as e:
        print(f'Error loading databases: {e}')
        raise

    return signals, dij_reduce, backtest

def plot_dij_signals(symbol: str):
    signals, _, _ = importbases()

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

def plot_signal_correlation(
    matrix,
    output_path='DIJ_signal_correlation.png',
):
    
    if matrix.empty or matrix.isna().all().all():
        print('No valid correlations to plot.')
        return

    fig, ax = plt.subplots(figsize=(20, 18))

    heatmap = ax.imshow(
        matrix.to_numpy(),
        cmap='RdBu_r',
        vmin=-1,
        vmax=1,
    )

    for row in range(len(matrix.index)):
        for col in range(len(matrix.columns)):
            value = matrix.iloc[row, col]

            if pd.notna(value):
                ax.text(
                    col,
                    row,
                    f'{value:.2f}',
                    ha='center',
                    va='center',
                    fontsize=7,
                    color='white' if abs(value) >= 0.6 else 'black',
            )
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_yticks(range(len(matrix.index)))
    ax.set_xticklabels(matrix.columns, rotation=90)
    ax.set_yticklabels(matrix.index)
    ax.set_title('DIJ Signal Correlation')

    fig.colorbar(heatmap, ax=ax, label='Correlation')
    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    return fig, ax

def plot_signal_clusters(
    clusters,
    output_path='DIJ_signal_clusters.png',
):
    fig, ax = plt.subplots(figsize=(14, 6))

    for cluster, group in clusters.groupby('Cluster'):
        ax.scatter(
            group['Symbol'],
            group['Cluster'],
            label=f'Cluster {cluster}',
            s=100,
        )

    ax.set_title('DIJ Signal Clusters')
    ax.set_xlabel('DIJ Contract')
    ax.set_ylabel('Cluster')
    ax.set_yticks(sorted(clusters['Cluster'].unique()))
    ax.tick_params(axis='x', labelrotation=90)
    ax.grid(axis='y', alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.show()

    return fig, ax

def plot_backtest():
    _, _, backtest = importbases()

    if backtest.empty:
        print('No backtest data available to plot.')
        return

    backtest = backtest.copy()
    backtest['pair'] = (
        backtest['long_contract'].astype(str)
        + ' x '
        + backtest['short_contract'].astype(str)
    )

    results = (
        backtest.groupby(['pair', 'strategy'], as_index=False)['pnl']
        .sum()
    )
    top_10 = results.nlargest(10, 'pnl').copy()

    colors = {'Long': 'steelblue', 'Short': 'darkorange'}
    bar_colors = top_10['strategy'].map(colors)

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(top_10['pair'], top_10['pnl'], color=bar_colors)

    ax.set_title('Top 10 Backtest Results')
    ax.set_xlabel('Spread Pair')
    ax.set_ylabel('PnL (USD)')
    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda value, _: f'${value / 1000 :,.0f}'.replace(',', ','))
    )

    
    min_pnl = min(0, top_10['pnl'].min())
    max_pnl = max(0, top_10['pnl'].max())
    margin = (max_pnl - min_pnl) * 0.08 or 1
    ax.set_ylim(min_pnl - margin, max_pnl + margin)

    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=45)

    legend_handles = [
        Patch(color=color, label=strategy)
        for strategy, color in colors.items()
        if strategy in top_10['strategy'].values
    ]
    ax.legend(handles=legend_handles, title='Strategy')

    fig.tight_layout()
    fig.savefig('DIJ_backtest_pnl.png', dpi=300, bbox_inches='tight')
    plt.show()

    return fig, ax

if __name__ == '__main__':

    plot_backtest()