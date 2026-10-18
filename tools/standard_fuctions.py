import json
import os
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import datetime, date

def bussiness_days_to_maturity(maturity_date, holidays_path=r'database\feriados_nacionais.json'):
    """
    Calculate the number of business days to maturity from today, excluding weekends and holidays.
    
    Parameters:
    - maturity_date: The maturity date of the DIJ contract in 'YYYY-MM-DD' format.
    - holidays_path: Path to the file containing national holidays.
    
    Returns:
    - business_days: The number of business days to maturity.
    """


    holidays_df = pd.read_json(holidays_path)

    date_col = 'Data' if 'Data' in holidays_df.columns else 'Date'

    cleaned_dates = pd.to_datetime(holidays_df[date_col], errors='coerce')
    cleaned_dates = cleaned_dates.dropna()
    holidays = cleaned_dates.dt.date.values
    holidays = np.array(holidays, dtype='datetime64[D]')

    today = np.datetime64(pd.Timestamp.now().date())
    maturity = np.datetime64(pd.to_datetime(maturity_date).date())
    
    # If the contract has already matured, return 0 business days
    if maturity <= today:
        return 0 

    business_days = np.busday_count(today, maturity, weekmask='1111100', holidays=holidays)
    
    return int(business_days)

def json_date_serializer(obj):
    """ Force dates to save strictly as YYYY-MM-DD strings without time """

    if isinstance(obj, (datetime, date)):
        return obj.strftime('%Y-%m-%d')
    
    raise TypeError(f"Type {type(obj)} not serializable")

def format_date_columns(df):
    """ Ensures any date column is saved as a clean YYYY-MM-DD string """

    for col in df.columns:

        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.strftime('%Y-%m-%d')

        elif not pd.api.types.is_numeric_dtype(df[col]):

            try:
                converted = pd.to_datetime(df[col], errors='raise', dayfirst=True, format='mixed')
                df[col] = converted.dt.strftime('%Y-%m-%d')
            except Exception:
                pass

    return df

def transform_to_json(path=str(), end_path=str()):
    """
    Detects the file extension and converts the file to JSON format.
    Supports: .csv, .xlsx, .xls, .txt
    """

    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    try:
        if ext in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
            df = format_date_columns(df)
            
        elif ext == '.csv':
            df = pd.read_csv(path, sep=",", encoding="utf-8")
            df = format_date_columns(df)
            
        elif ext == '.txt':
            with open(path, "r", encoding="utf-8") as file:
                lines = [line.strip() for line in file if line.strip()]
            data_to_save = [{"line": index + 1, "text": content} for index, content in enumerate(lines)]
            
        else:
            print(f"Error: '{ext}' not supported. Please use .xlsx, .xls, .csv or .txt")
            return

        if ext in ['.xlsx', '.xls', '.csv']:
            
            df = df.fillna("") 
            data_to_save = df.to_dict(orient="records")

        
        with open(end_path, "w", encoding="utf-8") as json_file:
            json.dump(data_to_save, json_file, ensure_ascii=False, indent=4, default=json_date_serializer)
            
        print(f"Success: File converted to {end_path}")

    except Exception as e:
        print(f"Error: {e}")