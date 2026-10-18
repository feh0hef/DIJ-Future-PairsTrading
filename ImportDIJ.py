#libraries
import os
import json
import requests
import datetime
import pandas as pd
import numpy as np



#global variables
df_request = [] #will receive the data from the request
url = "https://cotacao.b3.com.br/mds/api/v1/DerivativeQuotation/DI1" #B3 API URL
clm_rename = ["Symbol", "Desc", "Lower_Limit","Prv_Adjst", "Upper_Limit",
    "Opng_Price", "Min_Price", "Max_Price", "Avg_Price",
    "Last_Price", "Volume", "Mtry_Date", "Open_Cts", "Trades_Qty", 
    "Traded_Cts", "Code", "Last_Buy_Offer", "Market", "Last_Sell_Offer"] #Vetor to rename the columns
json_path = r"database\DIJHist.json" #path to save the json file
today = datetime.datetime.now().strftime("%Y-%m-%d") #get the current date
liquidity_months = [1, 4, 7, 10] #months with higher liquidity for DIJ contracts


def requestB3API():
    #request data from B3 APi
    try:
        rqts = requests.get(url)
    except requests.exceptions.RequestException as e:
        print("Error in request: ", e)
        exit()

    try:
        text = rqts.text
        json_rqts = json.loads(text)
        #print(json_rqts)
    except json.JSONDecodeError as e:
        print("Error decoding JSON: ", e)
        exit()

    try:
        #Extract and Transform in request data
        df_request = pd.json_normalize(json_rqts['Scty'])

        df_request = df_request.sort_values(by="asset.AsstSummry.mtrtyCode", ascending=True)
        #print(df_request.keys())

        df_request.columns = clm_rename
        
        df_request = df_request[pd.to_datetime(df_request['Mtry_Date'], errors='coerce').dt.month.isin(liquidity_months)].copy()

        df_request["Date"] = today
        df_request = df_request.replace({np.nan: "", "NaN": ""})

    except KeyError as e:
        print("Error in DataFrame processing: ", e)

    save_request(df_request, json_path)

    return df_request


def save_request(df_request=df_request, file_path=json_path):

    today_verify = df_request["Date"].iloc[0] if not df_request.empty else datetime.date.today().strftime("%Y-%m-%d")

    json_new_to_save = df_request.to_dict(orient="records")

    try:

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                with open(file_path, "r+", encoding="utf-8") as file:
                    try:
                        data = json.load(file)
                    
                        if not isinstance(data, list):
                            data = [data]
                    
                        today_check = any(item.get("Date") == today for item in data)
                        
                        if today_check:
                            print(f"Skipping save: Data for {today} already exists in historic.\n")
                            return 
                        
                        data.extend(json_new_to_save)

                    except json.JSONDecodeError:
                        print(f"Warning: {file_path} was corrupted. Resetting historic with new data.\n")
                        data = json_new_to_save

                    file.seek(0)
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.truncate()
        else:    
            if os.path.dirname(file_path):
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(json_new_to_save, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"Isn't possible to add new values in historic. \nError: {e}")

    return print("---")