from database.ImportDIJ import requestB3API
from statistics.stats import RunSignalDIJ
import pandas as pd

if __name__ == "__main__":

    try:
        requestB3API()  # Fetch and save DIJ data from B3 API

    except Exception as e:
        print(f"Error during API request: {e}")

    try:    
        data = pd.read_json(r'database\DIJHist.json')  # Load the saved DIJ data
        RunSignalDIJ(data)  # Run the signal calculation and save the results
        print("Process completed successfully.")
    except Exception as e:
        print("Process Failed in save signals")

        