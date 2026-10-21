from pathlib import Path

import pandas as pd

from tools.calculate_fuctions import signalDIJ


SIGNALS_PATH = Path(__file__).resolve().parent / 'DIJSignals.json'
KEY_COLUMNS = ['Date', 'Symbol']
COLUMNS = ['Symbol', 'Date', 'Sum_Signals']


def RunSignalDIJ(data, output_path=SIGNALS_PATH):
    """Append missing dated signals, using only observations available that day."""


    output_path = Path(output_path)
    source = data[['Symbol', 'Date', 'Last_Mid']].copy()
    source['Date'] = pd.to_datetime(source['Date'], errors='raise').dt.strftime('%Y-%m-%d')

    if source[KEY_COLUMNS + ['Last_Mid']].isna().any().any():
        raise ValueError('Signal input contains missing dates, symbols or rates.')
    if source.duplicated(KEY_COLUMNS).any():
        raise ValueError('Duplicate Date + Symbol keys in signal input.')

    if output_path.exists() and output_path.stat().st_size > 0:
        existing = pd.read_json(output_path, convert_dates=False)
        if existing.empty:
            existing = pd.DataFrame(columns=COLUMNS)
        else:
            existing = existing[COLUMNS].copy()
            existing['Date'] = pd.to_datetime(existing['Date'], errors='raise').dt.strftime('%Y-%m-%d')
            if existing[KEY_COLUMNS].isna().any().any():
                raise ValueError('Missing keys in signal history.')
            if existing.duplicated(KEY_COLUMNS).any():
                raise ValueError('Duplicate Date + Symbol keys in signal history.')
    else:
        existing = pd.DataFrame(columns=COLUMNS)

    existing_keys = set(zip(existing['Date'], existing['Symbol']))
    new_records = []

    for symbol, group in source.sort_values(KEY_COLUMNS).groupby('Symbol', sort=False):
        rates = group['Last_Mid'].tolist()
        for position, date in enumerate(group['Date']):
            if (date, symbol) in existing_keys:
                continue
            
            window = rates[max(0, position - 20):position + 1]
            signal = signalDIJ(window)
            new_records.append({
                'Symbol': symbol,
                'Date': date,
                'Sum_Signals': sum(value for value in signal[1:] if value is not None),
            })

    if not new_records:
        print('Signal history is up to date. No new records; no file was changed.')
        return existing

    new_data = pd.DataFrame(new_records, columns=COLUMNS)

    result = (new_data if existing.empty else pd.concat([existing, new_data], ignore_index=True))
    result = result.sort_values(KEY_COLUMNS, ignore_index=True)
    content = result.to_json(orient='records', indent=4, force_ascii=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix('.json.tmp')
    temporary_path.write_text(content, encoding='utf-8')
    temporary_path.replace(output_path)

    print(f'{len(new_records)} new signal records saved. Total: {len(result)} records.')

    return result
