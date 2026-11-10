from tools.calculate_fuctions import deviation, covariance
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import torch
import json
import os

data = pd.read_json(r'database\DIJSignals.json')
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


def cluster_signal_correlation(matrix=signal_correlation(), k=6):

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

def cov_inter_clusters(x_list: list, y_list: list, sample: bool = False) -> torch.Tensor:
    """
    Calculate the cross-covariance matrix between two clusters of potentially different sizes.
    Returns a PyTorch tensor matrix of shape (len(x_list), len(y_list)).
    """
    if not x_list or not y_list:
        return torch.tensor(0.0)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    X = torch.tensor(x_list, dtype=torch.float32, device=device)
    Y = torch.tensor(y_list, dtype=torch.float32, device=device)
    
    n_x = len(X)
    n_y = len(Y)

    avg_x = torch.mean(X)
    avg_y = torch.mean(Y)

    deviation_x = X - avg_x
    deviation_y = Y - avg_y

    matrix = torch.outer(deviation_x, deviation_y)

    div = (n_x * n_y - 1) if sample else (n_x * n_y)

    if div <= 0:
        raise ValueError("Insufficient data points for covariance calculation.")

    covariance_matrix = matrix / div

    return torch.round(covariance_matrix, decimals=4)

def run_inter_cluster_analysis(matrix: pd.DataFrame, clusters_df: pd.DataFrame, sample: bool = False) -> dict:
    """
    Orchestrates the cross-covariance loop between all distinct cluster combinations.
    Returns a dictionary mapped by (cluster_A, cluster_B) containing the resulting PyTorch Tensors.
    """
    unique_clusters = sorted(clusters_df['Cluster'].unique())
    covariances_dict = {}
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    for i in unique_clusters:
        for j in unique_clusters:
            if i != j:  
                symbols_A = clusters_df[clusters_df['Cluster'] == i]['Symbol'].tolist()
                symbols_B = clusters_df[clusters_df['Cluster'] == j]['Symbol'].tolist()
                
                
                data_A = matrix.loc[symbols_A].to_numpy()
                data_B = matrix.loc[symbols_B].to_numpy()
                
                
                X = torch.tensor(data_A, dtype=torch.float32, device=device)
                Y = torch.tensor(data_B, dtype=torch.float32, device=device)
                
                n_x = X.size(0)
                n_y = Y.size(0)
                
                
                dev_X = X - torch.mean(X, dim=0, keepdim=True)
                dev_Y = Y - torch.mean(Y, dim=0, keepdim=True)
                
                
                expanded_products = dev_X.unsqueeze(1) * dev_Y.unsqueeze(0)
                
                
                matrix_products = torch.mean(expanded_products, dim=2)
                
                
                div = (n_x * n_y - 1) if sample else (n_x * n_y)
                
                if div <= 0:
                    calculated_matrix = torch.tensor(0.0)
                else:
                    
                    calculated_matrix = (matrix_products * (n_x * n_y)) / div
                
                
                covariances_dict[(i, j)] = torch.round(calculated_matrix, decimals=4)
                
    return covariances_dict

def save_covariances_to_json(matrix: pd.DataFrame, clusters_df: pd.DataFrame, cov_results: dict, filename: str = "daily_covariance.json"):
    """
    Saves the computed covariance matrices to a JSON file.
    Maps matrix indices back to their real asset symbols.
    """
    db_folder = os.path.join(os.getcwd(), "database")
    os.makedirs(db_folder, exist_ok=True)
    
    negative_pairs_data = {}
    
    for (cluster_A, cluster_B), tensor_matrix in cov_results.items():
        
        symbols_A = clusters_df[clusters_df['Cluster'] == cluster_A]['Symbol'].tolist()
        symbols_B = clusters_df[clusters_df['Cluster'] == cluster_B]['Symbol'].tolist()
        
        cluster_key = f"{cluster_A}-{cluster_B}"
        pairs_list = []
        
        
        for i in range(len(symbols_A)):
            for j in range(len(symbols_B)):
                val = tensor_matrix[i, j].item()
                
                
                if val < 0:
                    pairs_list.append({
                        "symbol_A": symbols_A[i],
                        "symbol_B": symbols_B[j],
                        "covariance": val
                    })
        
        
        if pairs_list:
            negative_pairs_data[cluster_key] = pairs_list
            
    file_path = os.path.join(db_folder, filename)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(negative_pairs_data, f, indent=4)
        
    print(f"[SUCCESS] Negative covariance pairs successfully exported to: {file_path}")