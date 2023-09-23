import pandas as pd

def convert_to_heikinashi(df):
    # Calculate Heikin Ashi values
    ha_data = df.copy()
    ha_data['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4
    ha_data['HA_Open'] = (ha_data['Open'].shift(1) + ha_data['HA_Close'].shift(1)) / 2
    ha_data['HA_High'] = ha_data[['High', 'HA_Open', 'HA_Close']].max(axis=1)
    ha_data['HA_Low'] = ha_data[['Low', 'HA_Open', 'HA_Close']].min(axis=1)

    # Drop unnecessary columns
    ha_data.drop(['Open', 'High', 'Low', 'Close'], axis=1, inplace=True)
    
    return ha_data

'''
This File Will Contains all the Technical Indicatores which takes the input Prametrs 
and accordingly returns a new output dataframe along with the required technical columns 
'''