import pandas as pd
import numpy as np
from tools.standard_fuctions import bussiness_days_to_maturity
from tools.calculate_fuctions import DIJ_dv01, mid_rate, dv01_volume

data = pd.read_json(r'database\DIJHist.json')
df = data[["Symbol", "Mtry_Date", "Last_Buy_Offer", "Last_Sell_Offer", "Volume", "Date"]].copy()


df["Last_Buy_Offer"] = pd.to_numeric(df["Last_Buy_Offer"], errors='coerce').fillna(0)
df["Last_Sell_Offer"] = pd.to_numeric(df["Last_Sell_Offer"], errors='coerce').fillna(0)
df["Volume"] = pd.to_numeric(df["Volume"], errors='coerce').fillna(0)


v_days = np.vectorize(bussiness_days_to_maturity, excluded=['holidays_path'])
v_mid_rate = np.vectorize(mid_rate)
v_dv01 = np.vectorize(DIJ_dv01)
v_dv01_volume = np.vectorize(dv01_volume)


df["Bd"] = v_days(maturity_date=df["Mtry_Date"], start_date=df["Date"])


df["Mid_Rate"] = v_mid_rate(sell_rate=df["Last_Sell_Offer"], buy_rate=df["Last_Buy_Offer"])


df["Dv01"] = v_dv01(bd=df["Bd"], rate=df["Mid_Rate"], Spot=5.5)

df["Dv01_Volume"] = v_dv01_volume(dv01=df["Dv01"], volume=df["Volume"])

print(df.head(3))