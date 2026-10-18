#libraries
from ast import Return

import pandas as pd
import json
import requests

#global variables
df_request = [] #will receive the data from the request
url = "https://cotacao.b3.com.br/mds/api/v1/DerivativeQuotation/DI1" #B3 API URL
clm_rename = ["Symbol", "Desc", "Lower_Limit","Prv_Adjst", "Upper_Limit",
    "Opng_Price", "Min_Price", "Max_Price", "Avg_Price",
    "Last_Price", "Volume", "Mtry_Date", "Open_Cts", "Trades_Qty", 
    "Traded_Cts", "Code", "Last_Buy_Offer", "Market", "Last_Sell_Offer"] #Vetor to rename the columns

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
        print(df_request.head(3))

    except KeyError as e:
        print("Error in DataFrame processing: ", e)

    return df_request