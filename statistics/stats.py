#python -m statistics.stats
from tools.calculate_fuctions import signalDIJ
from database.ImportDIJ import save_request
import pandas as pd

data = pd.read_json(r'database\DIJHist.json')

def RunSignalDIJ(data):

    result_signals = []

    for symbol in data['Symbol'].unique():
        
        symbol_data = data[data['Symbol'] == symbol].sort_values(by='Date')
        
        signal = signalDIJ(symbol_data['Last_Buy_Offer'].tolist())
        
        if not isinstance(signal, list):
            continue
            
        date_ref = signal[0]
        
        valid_signals = [s for s in signal[1:] if s is not None]
        
        sum_signals = sum(valid_signals)
        
        result_signals.append({
            'Symbol': symbol,
            'Date': date_ref,
            'Sum_Signals': sum_signals
        })

    df_summed_signals = pd.DataFrame(result_signals)

    try:
        df_summed_signals.to_json(r'statistics\DIJSignals.json', orient='records')
        print("Signals saved successfully to statistics/DIJSignals.json")
    except Exception as e:
        print(f"Error saving JSON: {e}")

    return df_summed_signals

