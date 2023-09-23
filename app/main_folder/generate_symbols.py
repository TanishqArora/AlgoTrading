import pandas as pd
import datetime
import api_methods

all_symbols = pd.read_csv('../csv/all_symbols.csv', index_col = 0)
all_symbols['expiry'] = pd.to_datetime(all_symbols['expiry']).apply(lambda x: x.date())

def get_instrument_key_from_trading_symbol(trading_symbol):
    instrument_key = all_symbols[all_symbols['tradingsymbol'] == trading_symbol]['instrument_key'].values[0]
    return instrument_key

def get_trading_symbol_from_instrument_key(instrument_key):
    tradingsymbol = all_symbols[all_symbols['instrument_key'] == instrument_key]['tradingsymbol'].values[0]
    return tradingsymbol

def get_exchange_from_instrument_key(instrument_key):
    exchange = all_symbols[all_symbols['instrument_key'] == instrument_key]['exchange'].values[0]
    return exchange

def get_options_trading_symbol(Indx = 'NSE_INDEX|Nifty 50', expiry_week = 1, level= '1-ITM', ce_pe = 'CE'):

    # Create the expiry_date variable
    today = datetime.date.today()
    current_day = today.weekday()
    days_ahead = (3 - current_day) % 7 + expiry_week * 7
    next_thursday = today + datetime.timedelta(days=days_ahead)
    expiry_date = (next_thursday.strftime('%y%-m%d')).upper()

    # Extract Last Traded Price Using yfinance
    last_traded_price = int(api_methods.get_ltp_data(Indx))

    # create price_level variable
    level_split = level.split('-')
    if level_split[0] == 'ATM':
        price_level = ((last_traded_price // 50))*50
    elif level_split[1] == 'ITM' and ce_pe == 'CE':
        price_level = ((last_traded_price // 50)  - int(level_split[0]))*50
    elif level_split[1] == 'ITM' and ce_pe == 'PE':
        price_level = ((last_traded_price // 50)  + int(level_split[0]))*50
    elif level_split[1] == 'OTM' and ce_pe == 'CE':
        price_level = ((last_traded_price // 50)  - int(level_split[0]))*50
    elif level_split[1] == 'OTM' and ce_pe == 'PE':
        price_level = ((last_traded_price // 50)  + int(level_split[0]))*50
    else:
        price_level = ((last_traded_price // 50))*50

    # Create final_symbol
    final_symbol = 'NIFTY' + str(expiry_date) + str(price_level) + str(ce_pe)

    return final_symbol
