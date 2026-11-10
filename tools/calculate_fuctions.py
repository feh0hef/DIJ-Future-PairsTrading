from typing import List, Union
import datetime
import pandas as pd


def DIJ_dv01(bd=int, rate=float, FV=100000, Spot=float):
    """
    Calculate the DV01 (Dollar Value of 01) for a DIJ future contract.
    
    Parameters:
    - bd: bussines days to maturity of the DIJ contract.
    - rate: The price of the DIJ contract.
    - FV: The FV BRL of the DIJ contract.
    - Spot: The spot price BRLUSD
    
    Returns:
    - dv01: The calculated DV01 value in USD.
    """

    derivate = -(bd/252) * FV / (1 + rate/100)**((bd/252)+1)

    dv01 = round(abs(derivate*0.0001) / Spot,2)
    
    return dv01

def Spread_DIJ(data: pd.DataFrame, flattened_pairs: list, day_0, last_day) -> list:
    """
    Calculate the spread between two DIJ future contracts for day_0 and last_day.
    Automatically detects long and short tenors based on business days (bd).
    
    Returns:
    - results: A list of dicts with calculated spread values (in bps) and metadata.
    """
    results = []
    
    for pair in flattened_pairs:
        symbol_A = pair["symbol_A"]
        symbol_B = pair["symbol_B"]
        
        
        hist_A = data[data['Symbol'] == symbol_A]
        hist_B = data[data['Symbol'] == symbol_B]
        
        
        if hist_A.empty or hist_B.empty:
            continue
            
        
        bd_A = hist_A.iloc[-1]['bd']
        bd_B = hist_B.iloc[-1]['bd']
        
        if bd_A > bd_B:
            long_hist, short_hist = hist_A, hist_B
            long_sym, short_sym = symbol_A, symbol_B
        else:
            long_hist, short_hist = hist_B, hist_A
            long_sym, short_sym = symbol_B, symbol_A
            
        
        p_long_0 = long_hist[long_hist['Date'] == day_0]['Avg_Price']
        p_short_0 = short_hist[short_hist['Date'] == day_0]['Avg_Price']
        
        p_long_last = long_hist[long_hist['Date'] == last_day]['Avg_Price']
        p_short_last = short_hist[short_hist['Date'] == last_day]['Avg_Price']
        
        
        if not p_long_0.empty and not p_short_0.empty and not p_long_last.empty and not p_short_last.empty:
            
            
            spread_0 = round(float(p_long_0.iloc[0]) - float(p_short_0.iloc[0]), 2) * 100
            spread_last = round(float(p_long_last.iloc[0]) - float(p_short_last.iloc[0]), 2) * 100
            
            results.append({
                "cluster_pair": pair["cluster_pair"],
                "symbol_A": symbol_A,
                "symbol_B": symbol_B,
                "long_contract": long_sym,
                "short_contract": short_sym,
                "spread_day0_bps": spread_0,
                "spread_last_day_bps": spread_last,
                "spread_change_bps": round(spread_last - spread_0, 2)
            })
            
    return results

def dv01_volume(dv01=float, volume=float):
    """
    Calculate the DV01 volume for a DIJ future contract.
    
    Parameters:
    - dv01: The DV01 value of the DIJ contract.
    - volume: The volume of the DIJ contract.
    
    Returns:
    - dv01_volume: The calculated DV01 volume value in USD.
    """

    dv01_volume = round(dv01 * volume, 1)
    
    return dv01_volume

def mid_rate(sell_rate=float, buy_rate=float):
    """
    Calculate the mid rate between two rates.
    
    Parameters:
    - sell_rate: The selling rate.
    - buy_rate: The buying rate.
    
    Returns:
    - mid_rate: The calculated mid rate value.
    """

    mid_rate = round((sell_rate + buy_rate) / 2, 4)
    
    return mid_rate

def average(RateOrSpreads: list):
    """
    Calculate the average rate/spread from a list of rates/spreads.
    
    Parameters:
    - rates: A list of rates.
    - spreads: A list of spreads.
    
    Returns:
    avg: The calculated average  value.
    """
    if not RateOrSpreads:
        return 0.0

    avg = sum(RateOrSpreads) / len(RateOrSpreads)
    
    return avg

def deviation(RateOrSpreads: list):
    """
    Calculate the standard deviation of a list of rates/spreads.
    
    Parameters:
    - rates: A list of rates.
    - spreads: A list of spreads.
    
    Returns:
    std_dev: The calculated standard deviation value.
    """
    if not RateOrSpreads:
            return 0.0

    avg = average(RateOrSpreads)

    variance = sum((x - avg) ** 2 for x in RateOrSpreads) / len(RateOrSpreads)

    std_dev = round(variance ** 0.5, 4)
    
    return std_dev

def covariance(x_list: list, y_list: list, sample: bool = True):
    """
    Calculate the covariance between two DIJs
    """
    
    if not x_list or not y_list:
        return 0.0
    if len(x_list) != len(y_list):
        raise ValueError("X,Y lists must have the same length.")
        
    n = len(x_list)
  
    avg_x = average(x_list)
    avg_y = average(y_list)
    
    total_sum = sum((x - avg_x) * (y - avg_y) for x, y in zip(x_list, y_list))
    
    div = (n - 1) if sample else n
    
    if div <= 0:
        return 0.0
        
    return round(total_sum / div, 4)

def signalDIJ(x_list: list):
    """
    Calculate the trend signal for DIJ.
    
    Returns:
    - signal: A list containing [date, 1d_signal, 1W_signal, 1Mo_signal]
    """
    
    if not x_list:
        return 0.0

    dateref = datetime.datetime.now().strftime("%Y-%m-%d")
  
    last_value = x_list[-1]
    signal: List[Union[str, int, None]] = [dateref]

    parameters = [-2, -6, -21]  # 1 day, 1 week, and 1 month ago

    for param in parameters:
        
        if len(x_list) < abs(param):
            signal.append(None)
        else:
            previous_value = x_list[param]
            
            if last_value > previous_value:
                signal.append(1)
            elif last_value < previous_value:
                signal.append(-1)
            else:
                signal.append(0)

    return signal
