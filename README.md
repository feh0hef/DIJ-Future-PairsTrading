Dear GPT wrote this README.
Honestly, a boring work -- thanks GPT

--------------------

# DIJ Future Pairs Trading

A research project for analyzing B3 DI1 futures, including market data collection, signal calculation, inter-cluster covariance analysis, and pairs backtesting.

## Execution workflow

The recommended entry point is `orchestrator.py`. It runs three scripts in sequence, using the project root as the working directory:

```text
orchestrator.py
    ├── main.py          fetches data, runs ETL, and updates signals
    ├── interactions.py  calculates correlations, clusters, and negative covariances
    └── pairs.py         requests a start date and runs the backtest
```

The orchestrator checks that each script exists and stops if a process exits with a non-zero status. Note that `main.py` catches exceptions, prints an error, and returns without setting a failure exit code. As a result, an internal error in this stage may not stop the orchestrator from continuing.

### 1. `main.py` — data collection, ETL, and signals

1. `database/ImportDIJ.py` queries the B3 DI1 quotation API, selects contracts maturing in January, April, July, and October, and updates `database/DIJHist.json`. If records for the current date already exist, saving that day is skipped.
2. `database/ETL.py` normalizes dates, prevents duplicate `Date` and `Symbol` records, and calculates `Last_Mid`, business days to maturity (`bd`), and DV01. The processed data is saved to `database/DIJ_ETL.json`.
3. `statistics/stats.py` calculates signals for each contract and date from `Last_Mid`, then updates `database/DIJSignals.json`.

### 2. `interactions.py` — correlations, clusters, and covariance

1. `statistics/cov.py` loads signals from `database/DIJSignals.json` and builds a correlation matrix across contracts.
2. KMeans groups the contracts into six clusters.
3. The analysis calculates covariances between different clusters and saves pairs with negative covariance to `database/daily_covariance.json`.

### 3. `pairs.py` — spreads and backtest

1. `pairDIJ/findP.py` reads `database/daily_covariance.json` and `database/DIJ_ETL.json`.
2. The program prompts for a start date in `YYYY-MM-DD` format. The date must exist in the ETL data. The end date is the latest date available in that file.
3. `pairDIJ/backtest.py` calculates spread changes and simulates `Long` and `Short` scenarios using a fixed DV01 of 5,000.
4. Results are saved to `database/backtest_results.json`.

The backtest is a simulation; it does not submit orders to a broker or to B3.

## Project structure

```text
.
├── database/
│   ├── __init__.py
│   ├── ImportDIJ.py              # Queries B3 and updates the raw data history
│   ├── ETL.py                    # Normalizes and processes collected data
│   ├── DIJHist.json              # Raw B3 data history
│   ├── DIJ_ETL.json              # Processed market data
│   ├── DIJSignals.json           # Signals by contract and date
│   ├── daily_covariance.json     # Pairs with negative inter-cluster covariance
│   ├── backtest_results.json     # Long/Short backtest results
│   ├── feriados_nacionais.xls    # Tabular source for the holiday calendar
│   └── feriados_nacionais.json   # Holidays used in business-day calculations
├── graphs/
│   └── graphs.py                 # Signal, correlation, cluster, and backtest plots
├── pairDIJ/
│   ├── findP.py                  # Finds pairs and calculates spreads over a date range
│   └── backtest.py               # Runs and saves the backtest
├── statistics/
│   ├── __init__.py
│   ├── cov.py                    # Correlation, clustering, and inter-cluster covariance
│   └── stats.py                  # Signal generation and persistence
├── tools/
│   ├── __init__.py
│   ├── calculate_fuctions.py     # Mid rate, DV01, spread, covariance, and signal calculations
│   └── standard_fuctions.py      # Business days, holidays, and data conversion utilities
├── interactions.py               # Entry point for cluster analysis
├── main.py                       # Entry point for data collection, ETL, and signals
├── pairs.py                      # Entry point for the backtest
├── orchestrator.py               # Runs main.py, interactions.py, and pairs.py
└── requirements.txt              # Declared Python dependencies
```

Running the pipeline overwrites `database/daily_covariance.json` and `database/backtest_results.json`. Make copies if you need to keep previous results.

## Installation

From the repository root, create and activate a virtual environment in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Running the project

With the virtual environment activated, run this from the repository root:

```powershell
python orchestrator.py
```

When the backtest prompts for a start date, enter a date present in `database/DIJ_ETL.json`, for example:

```text
Enter the start date (YYYY-MM-DD): 2026-01-05
```

You can also run the stages individually, in this order:

```powershell
python main.py
python interactions.py
python pairs.py
```

`interactions.py` depends on `database/DIJSignals.json`; `pairs.py` depends on `database/daily_covariance.json` and `database/DIJ_ETL.json`.

## Plots

Plots are separate from the orchestrator. To run the backtest plot defined in the main block of `graphs/graphs.py`, execute this from the repository root:

```powershell
python -m graphs.graphs
```

The module reads `database/DIJSignals.json`, `database/DIJ_ETL.json`, and `database/backtest_results.json`. The backtest plot is saved as `DIJ_backtest_pnl.png` in the repository root. The file also provides functions for plotting an individual contract's signals, correlations, and clusters.

## Data and assumptions

- `main.py` needs internet access to query the B3 API.
- Business-day calculations depend on `database/feriados_nacionais.json`.
- Backtest assumptions, including the fixed DV01 of 5,000, are defined in the code and should be reviewed when interpreting results.
- Results are for research purposes and do not guarantee future performance.
