from pairDIJ.backtest import run_spread_backtest_pytorch

if __name__ == "__main__":
    df_pnl = run_spread_backtest_pytorch()
    
    print("\n" + "[SUCCESS] Backtest completed successfully. Results saved to 'backtest_results.json'.")
