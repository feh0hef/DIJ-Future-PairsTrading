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

def Spread_DIJ(Long_tenor=float, Short_tenor=float):
    """
    Calculate the spread between two DIJ future contracts.
    
    Parameters:
    - Long_tenor: The price of the long DIJ contract.
    - Short_tenor: The price of the short DIJ contract.
    
    Returns:
    - spread: The calculated spread value (in bps).
    """

    spread = round(Long_tenor - Short_tenor, 2)*100
    
    return spread

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

    mid_rate = round((sell_rate + buy_rate) / 2, 2)
    
    return mid_rate