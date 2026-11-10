import sys
import os
import json
import torch
import pandas as pd

from PairDIJ.findP import find_negative_pairs_spreads

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
    print("Starting PyTorch Spread Backtest engine...")
    

    spread_values = find_negative_pairs_spreads()
    if not spread_values:
        print("[WARNING] No spread values found to backtest.")
        return pd.DataFrame()
        
  
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
 
    DV01_FIXED = 5000.0
    
  
    spread_0 = torch.tensor([p["spread_day0_bps"] for p in spread_values], dtype=torch.float32, device=device)
    spread_last = torch.tensor([p["spread_last_day_bps"] for p in spread_values], dtype=torch.float32, device=device)
    

    delta_spread = spread_last - spread_0
    
    #pnl = dv01 * delta 
    pnl_long = DV01_FIXED * delta_spread 
    pnl_short = DV01_FIXED * (-delta_spread)  
    
    
    delta_list = torch.round(delta_spread, decimals=2).cpu().tolist()
    pnl_long_list = torch.round(pnl_long, decimals=2).cpu().tolist()
    pnl_short_list = torch.round(pnl_short, decimals=2).cpu().tolist()
    
    backtest_results = []

    for idx, pair in enumerate(spread_values):

        # Long Scenario
        backtest_results.append({
            "cluster_pair": pair["cluster_pair"],
            "symbol_A": pair["symbol_A"],
            "symbol_B": pair["symbol_B"],
            "long_contract": pair["long_contract"],
            "short_contract": pair["short_contract"],
            "delta_spread_bps": delta_list[idx],
            "strategy": "Long",
            "pnl": pnl_long_list[idx]
        })
        
        # Short Scenario
        backtest_results.append({
            "cluster_pair": pair["cluster_pair"],
            "symbol_A": pair["symbol_A"],
            "symbol_B": pair["symbol_B"],
            "long_contract": pair["long_contract"],
            "short_contract": pair["short_contract"],
            "delta_spread_bps": delta_list[idx],
            "strategy": "Short",
            "pnl": pnl_short_list[idx]
        })
        
    df_results = pd.DataFrame(backtest_results)

    save_backtest_to_json(backtest_results, filename="backtest_results.json")
        
    return df_results
