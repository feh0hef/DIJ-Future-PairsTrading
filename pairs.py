from PairDIJ.backtest import run_spread_backtest_pytorch

if __name__ == "__main__":
    df_pnl = run_spread_backtest_pytorch()
    
    print("\n" + "="*30)
    print("PYTORCH BACKTEST RESULTS SUMMARY (Top 15 Most Profitable Scenarios)")
    print("="*30)
    

    top_trades = df_pnl.sort_values(by="pnl", ascending=False).head(15)
    
    for idx, row in top_trades.iterrows():
        print(f"Pair: {row['symbol_A']} vs {row['symbol_B']} ({row['cluster_pair']})")
        print(f"  Long Tenor: {row['long_contract']} | Short Tenor: {row['short_contract']}")
        print(f"  Delta Spread: {row['delta_spread_bps']:.2f} bps | Strategy: {row['strategy']}")
        print(f"  Calculated PnL: USD {row['pnl']:,.2f}")
        print("-" * 30)
