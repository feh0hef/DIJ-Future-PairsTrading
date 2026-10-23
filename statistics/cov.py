from tools.calculate_fuctions import deviation, covariance
import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

data = pd.read_json(r'statistics\DIJSignals.json')
min_observations = len(data['Date'].unique())

def signal_correlation(min_observations=min_observations,data=data):
    
    signals = data.copy()
    signals['Date'] = pd.to_datetime(signals['Date'])

    table = signals.pivot(
        index='Date',
        columns='Symbol',
        values='Sum_Signals',
    ).sort_index()

    symbols = table.columns.tolist()
    matrix = pd.DataFrame(
        float('nan'),
        index=symbols,
        columns=symbols,
    )

    for i, symbol_x in enumerate(symbols):
        for symbol_y in symbols[i:]:
            
            pair = pd.concat(
                [table[symbol_x], table[symbol_y]],
                axis=1,
            ).dropna()

            if len(pair) < min_observations:
                continue

            x = pair.iloc[:, 0].tolist()
            y = pair.iloc[:, 1].tolist()

            std_x = deviation(x)
            std_y = deviation(y)

            if std_x == 0 or std_y == 0:
                continue

            correlation = (
                covariance(x, y, sample=False) / (std_x * std_y)
            )

            matrix.loc[symbol_x, symbol_y] = correlation
            matrix.loc[symbol_y, symbol_x] = correlation

    return matrix


def cluster_signal_correlation(matrix=signal_correlation(), k=int):

    profiles = matrix.dropna(axis=0, how='all')
    profiles = profiles.loc[profiles.index, profiles.index]

    if len(profiles) < k:
        raise ValueError(f'At least {k} valid contracts are required.')

    if profiles.isna().any().any():
        raise ValueError(
            'The correlation matrix contains missing values. '
            'Use contracts with sufficient overlapping observations.'
        )

    if not np.isfinite(profiles.to_numpy()).all():
        raise ValueError('The correlation matrix contains invalid values.')

    if len(profiles.drop_duplicates()) < k:
        raise ValueError(f'At least {k} distinct correlation profiles are required.')

    model = KMeans(
        n_clusters=k,
        random_state=30,
        n_init=15,
    )

    labels = model.fit_predict(profiles.to_numpy())

    clusters = pd.DataFrame({
        'Symbol': profiles.index,
        'Cluster': labels,
    }).sort_values(['Cluster', 'Symbol'], ignore_index=True)

    return clusters, model
