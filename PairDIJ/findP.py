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
    last_day = dates_sorted[-1]

    day_0_input = input("Enter the start date (YYYY-MM-DD): ").strip()
    try:
        day_0 = pd.to_datetime(day_0_input, format="%Y-%m-%d", errors="raise")
    except ValueError as exc:
        raise ValueError("The start date must use the YYYY-MM-DD format.") from exc

    if day_0 not in data['Date'].values:
        raise ValueError(f"No data available for the start date {day_0_input}.")

    spread_values = Spread_DIJ(data, flattened_pairs, day_0, last_day)
    
    return spread_values