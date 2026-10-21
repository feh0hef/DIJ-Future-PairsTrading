import json
import os
import pandas as pd
import numpy as np
from pandas.tseries.offsets import BDay
from datetime import datetime, date

def bussiness_days_to_maturity(
    maturity_date,
    start_date=None,
    holidays_path=r'database\feriados_nacionais.json',
    _cached_holidays=[None]
):
    """
    Calculate business days to maturity, excluding weekends and holidays.
    Accept scalar dates or arrays of dates.
    """
    
    if _cached_holidays[0] is None:
        holidays_df = pd.read_json(holidays_path)
        date_col = 'Data' if 'Data' in holidays_df.columns else 'Date'

        cleaned_dates = pd.to_datetime(
            holidays_df[date_col], errors='coerce'
        ).dropna()

        _cached_holidays[0] = cleaned_dates.to_numpy(
            dtype='datetime64[D]'
        )

    holidays = _cached_holidays[0]

    if start_date is None:
        start_date = pd.Timestamp.now().normalize()

    start = np.asarray(
        pd.to_datetime(start_date), dtype='datetime64[D]'
    )
    maturity = np.asarray(
        pd.to_datetime(maturity_date), dtype='datetime64[D]'
    )

    business_days = np.busday_count(
        start,
        maturity,
        weekmask='1111100',
        holidays=holidays
    )

    business_days = np.maximum(business_days, 0)

    return (
        int(business_days)
        if business_days.ndim == 0
        else business_days
    )

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

def delete_dij_values():
    file_path = r'database\DIJHist.json'
    
    
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    value_to_remove = input("Enter the date to remove from the JSON file (YYYY-MM-DD): ")

    initial_count = len(data)
    filtered_data = [item for item in data if item.get("Date") != value_to_remove]
    final_count = len(filtered_data)
    removed_count = initial_count - final_count

    if removed_count > 0:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(filtered_data, file, ensure_ascii=False, indent=4)
        print(f"Process completed successfully! Records removed: {removed_count}")
    else:
        print("No records found for the specified date. The file was not modified.")
