from pairDIJ.backtest import (
    run_spread_backtest_pytorch,
    top_5_by_operation
)


if __name__ == "__main__":
    df_pnl = run_spread_backtest_pytorch()

    print("\n[SUCCESS] Backtest completed successfully. Results saved to 'backtest_results.json'.")

    top_5_by_operation()