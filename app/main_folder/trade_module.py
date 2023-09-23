import requests
import api_methods

ACCESS_TOKEN = api_methods.get_access_token()


class Trade:

    def __init__(self, symbol, quantity):
        self.symbol = symbol
        self.quantity = quantity
    
    def place_order(self, type_, order_type, price,trigger_price_factor):
        URL = 'https://api-v2.upstox.com/order/place'

        headers = {
            'accept':'application/json',
            'Api-Version': '2.0',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + ACCESS_TOKEN
        }

        if order_type =='SL':
            data = {
                "quantity": self.quantity,
                "product": "I",
                "validity": "DAY",
                "price": price,
                "tag": "string",
                "instrument_token": self.symbol,
                "order_type": order_type,
                "transaction_type": type_,
                "disclosed_quantity": 0,
                "trigger_price": price + trigger_price_factor,
                "is_amo": False
            }
        else:
            data = {
                "quantity": self.quantity,
                "product": "I",
                "validity": "DAY",
                "price": price,
                "tag": "string",
                "instrument_token": self.symbol,
                "order_type": order_type,
                "transaction_type": type_,
                "disclosed_quantity": 0,
                "trigger_price": 0,
                "is_amo": False
            }

        response = requests.post(URL, headers=headers, params=None, json=data)
        print(response.json())
        return response.json()['data']['order_id']
    
    def modify_order(self, order_id, order_type, price,trigger_price_factor = None):
        url = 'https://api-v2.upstox.com/order/modify'
        headers = {
            'accept': 'application/json',
            'Api-Version': '2.0',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + ACCESS_TOKEN
        }
        if trigger_price_factor is None:
            data = {
                "quantity": self.quantity,
                "validity": "DAY",
                "price": price,
                "order_id": order_id,
                "order_type": order_type,
                "disclosed_quantity": 0,
                "trigger_price": price + 0.05
            }
        else:
            data = {
                "quantity": self.quantity,
                "validity": "DAY",
                "price": price,
                "order_id": order_id,
                "order_type": order_type,
                "disclosed_quantity": 0,
                "trigger_price": price + trigger_price_factor
            }

        response = requests.put(url, headers=headers, json=data)
        print(response.json())
        return response.json()['data']['order_id']
    
    # Actual Functions to be used in Stratagies
    def buy_limit_order(self, buy_price,trigger_price_factor=0.05):
        buy_limit_order_id = self.place_order('BUY', 'LIMIT', buy_price,trigger_price_factor)
        print(f'Placed Buy Order @ {buy_price}')
        return buy_limit_order_id
    
    def sell_limit_order(self, sell_price,trigger_price_factor=0.05):
        sell_limit_order_id = self.place_order('SELL', 'LIMIT', sell_price,(-1)*trigger_price_factor)
        print(f'Placed Sell Order @ {sell_price}')
        return sell_limit_order_id

    def stop_loss_sell_order(self, sl_price,trigger_price_factor=0.05):
        stop_loss_order_id = self.place_order('SELL', 'SL', sl_price,trigger_price_factor)
        print(f'Placed Stop Loss Sell Order @ {sl_price}')
        return stop_loss_order_id
    
    def stop_loss_buy_order(self, sl_price,trigger_price_factor=0.05):
        stop_loss_order_id = self.place_order('BUY', 'SL', sl_price,(-1)*trigger_price_factor)
        print(f'Placed Stop Loss Buy Order @ {sl_price}')
        return stop_loss_order_id
    
    def modify_to_market_order(self,buy_sell_limit_order_id,type_):

        modified_market_order_id = self.modify_order(buy_sell_limit_order_id, 'MARKET', 0)
        if type_ == 'BUY':
            print(f'Modified Buy Order To Market Buy Order')
        if type_ == 'SELL':
            print(f'Modified Sell Order To Market Sell Order')
        elif type_ == 'SL-BUY':
            print(f'Modified Stop Loss Buy Order To Market Buy Order')
        elif type_ == 'SL-SELL':
            print(f'Modified Stop Loss Sell Order To Market Sell Order')
        else:
            print(f'No Type Given But order id {buy_sell_limit_order_id} is Modified To Market Order')

        return modified_market_order_id
    
    def modify_stop_loss_order(self, stop_loss_order_id, modified_sl_trgt_price,type_,trigger_price_factor=0.05):

        if type_ == 'BUY':
            modify_stop_loss_target_id = self.modify_order(stop_loss_order_id, 'SL', modified_sl_trgt_price,(-1)*trigger_price_factor)
            print(f'Modified Buy Order To Stop Loss Buy Order @ {modified_sl_trgt_price}')
        if type_ == 'SELL':
            modify_stop_loss_target_id = self.modify_order(stop_loss_order_id, 'SL', modified_sl_trgt_price,trigger_price_factor)
            print(f'Modified Sell Order To Stop Loss Sell Order @ {modified_sl_trgt_price}')
        elif type_ == 'SL-BUY':
            modify_stop_loss_target_id = self.modify_order(stop_loss_order_id, 'SL', modified_sl_trgt_price,(-1)*trigger_price_factor)
            print(f'Modified Stop Loss Buy Order To @ {modified_sl_trgt_price}')
        elif type_ == 'SL-SELL':
            modify_stop_loss_target_id = self.modify_order(stop_loss_order_id, 'SL', modified_sl_trgt_price,trigger_price_factor)
            print(f'Modified Stop Loss Sell Order To @ {modified_sl_trgt_price}')
        else:
            print(f'No Type Given But order id {stop_loss_order_id} is Modified @ {modified_sl_trgt_price}')
        
        return modify_stop_loss_target_id
    
    def check_condition_to_force_sell(self,order_status, selling_price,ltp):

        if order_status != 'Completed' and ltp < selling_price:
            return True
        else:
            return False

    def check_condition_to_force_buy(self,order_status, buy_price,ltp):

        if order_status != 'Completed' and ltp > buy_price:
            return True
        else:
            return False