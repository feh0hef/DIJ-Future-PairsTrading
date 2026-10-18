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
