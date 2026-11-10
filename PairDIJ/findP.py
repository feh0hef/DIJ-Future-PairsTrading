import pandas as pd
import numpy as np
import json

from tools.calculate_fuctions import Spread_DIJ

def find_negative_pairs_spreads():

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

    dates_sorted = sorted(data['Date'].unique())
    day_0 = dates_sorted[0]
    last_day = dates_sorted[-1]

    spread_values = Spread_DIJ(data, flattened_pairs, day_0, last_day)
    return spread_values