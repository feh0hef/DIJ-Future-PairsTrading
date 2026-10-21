from pathlib import Path
import pandas as pd
from tools.calculate_fuctions import mid_rate, DIJ_dv01
from tools.standard_fuctions import bussiness_days_to_maturity

BASE_DIR = Path(__file__).resolve().parent
RAW_PATH = BASE_DIR / 'DIJHist.json'
ETL_PATH = BASE_DIR / 'DIJ_ETL.json'

KEY_COLUMNS = ['Date', 'Symbol']
DATE_COLUMNS = ['Date', 'Mtry_Date']

def normalize_dates(data):
    data = data.copy()

    for column in DATE_COLUMNS:
        data[column] = pd.to_datetime(
            data[column], errors='raise'
        ).dt.strftime('%Y-%m-%d')

    return data

def DIJ_Reduce(data, output_path=ETL_PATH, spot=5.5):
    output_path = Path(output_path)
    raw = normalize_dates(data)

    if raw[KEY_COLUMNS].isna().any().any():
        raise ValueError('Date and Symbol cannot contain missing values.')

    if raw.duplicated(KEY_COLUMNS).any():
        raise ValueError('Duplicate Date + Symbol keys in raw data.')

    if output_path.exists() and output_path.stat().st_size > 0:
        existing = normalize_dates(
            pd.read_json(output_path, convert_dates=False)
        )

        if existing[KEY_COLUMNS].isna().any().any():
            raise ValueError('Missing keys in ETL data.')

        if existing.duplicated(KEY_COLUMNS).any():
            raise ValueError('Duplicate Date + Symbol keys in ETL data.')

        existing_keys = pd.MultiIndex.from_frame(
            existing[KEY_COLUMNS]
        )
        raw_keys = pd.MultiIndex.from_frame(raw[KEY_COLUMNS])

        new_data = raw.loc[~raw_keys.isin(existing_keys)].copy()
    else:
        existing = pd.DataFrame()
        new_data = raw

    if new_data.empty:
        print('No new records to process.')
        return existing

    processed = new_data[
        [
            'Date',
            'Symbol',
            'Mtry_Date',
            'Min_Price',
            'Max_Price',
            'Avg_Price',
        ]
    ].copy()

    processed['Last_Mid'] = mid_rate(
        buy_rate=new_data['Last_Buy_Offer'],
        sell_rate=new_data['Last_Sell_Offer'],
    )

    processed['bd'] = bussiness_days_to_maturity(
        maturity_date=new_data['Mtry_Date'],
        start_date=new_data['Date'],
    )

    processed['Dv01'] = DIJ_dv01(
        bd=processed['bd'],
        rate=processed['Last_Mid'],
        Spot=spot,
    )

    result = pd.concat(
        [existing, processed],
        ignore_index=True,
    ).sort_values(KEY_COLUMNS, ignore_index=True)

    content = result.to_json(
        orient='records',
        indent=4,
        force_ascii=False,
        double_precision=15,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix('.json.tmp')
    temporary_path.write_text(content, encoding='utf-8')
    temporary_path.replace(output_path)

    print(
        f'{len(processed)} new records processed. '
        f'Total: {len(result)} records.'
    )

    return result