from pathlib import Path

import pandas as pd

from database.ImportDIJ import requestB3API
from database.ETL import DIJ_Reduce
from statistics.stats import RunSignalDIJ

BASE_DIR = Path(__file__).resolve().parent

def main():
    
    try:
        requestB3API()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    try:
        raw_data = pd.read_json(
            BASE_DIR / 'database' / 'DIJHist.json',
            convert_dates=False,
        )
        etl_data = DIJ_Reduce(raw_data)
    except Exception as e:
        print(f"Error processing ETL data: {e}")
        return

    try:
        RunSignalDIJ(etl_data)
    except Exception as e:
        print(f"Error calculating or saving signals: {e}")
        return

    print("Process completed successfully.")


if __name__ == "__main__":
    main()