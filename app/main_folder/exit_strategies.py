import api_methods
import time

class exit_strategy:
    """
    These Strategies are only used for scalping with quick profits and limited losses exits
    """

    def __init__(self, trade_instance,sl_percent = 0.02,target_percent = 0.01,trigger_price_factor=0.05,factor = 0.01,big_move=False,forced_entry=False):
        self.trade = trade_instance
        self.sl_percent = sl_percent
        self.target_percent = target_percent
        self.trigger_price_factor = trigger_price_factor
        self.factor = factor
        self.big_move = big_move
        self.forced_entry = forced_entry
        
    def buy_trail_stop_loss(self):
        should_exit = False

        print('********************************* Buy And Trail Stop Loss Function Called *********************************')
        buy_price = api_methods.get_ltp_websocket(self.trade.symbol)
        while buy_price is None:
            buy_price = api_methods.get_ltp_websocket(self.trade.symbol)
            time.sleep(0.1)

        buy_limit_order_id = self.trade.buy_limit_order(buy_price)  # Fixed function call
        sl_price = api_methods.convert_to_nearest(buy_price * (1 - self.sl_percent))
        sl_target_price = api_methods.convert_to_nearest(buy_price * (1 + self.target_percent))
        print(f'Buy Price: {buy_price}, sl_price: {sl_price}, sl_target_price: {sl_target_price}')

        print('Checking Buy Order Status.......')
        order_status = 'Pending'
        while order_status != 'Completed':

            order_status = api_methods.get_order_status_websocket(buy_limit_order_id)
            ltp = api_methods.get_ltp_websocket(self.trade.symbol)

            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            if order_status != 'Completed' and ltp > buy_price * 1.005:
                if not self.forced_entry:
                    print(f'Cancelling Buy Limit Order as Price Became : {ltp}')
                    api_methods.cancel_order(buy_limit_order_id)
                    order_status = 'Completed'
                    should_exit = True
                    break

                if self.forced_entry:
                    print(f'Placing Forced Market Buy Order as LTP Became: {ltp}')
                    buy_market_order_id = self.trade.modify_to_market_order(buy_limit_order_id,'BUY')

                    market_buy_price = api_methods.get_order_avg_price(buy_market_order_id)
                    while market_buy_price is None:
                        market_buy_price = api_methods.get_order_avg_price(buy_market_order_id)
                        time.sleep(0.5)

                    sl_price = api_methods.convert_to_nearest(market_buy_price * (1 - self.sl_percent))
                    sl_target_price = api_methods.convert_to_nearest(market_buy_price * (1 + self.target_percent))
                    buy_limit_order_id = buy_market_order_id
                    print(f'Market Buy Price: {market_buy_price}, sl_price: {sl_price}, sl_target_price: {sl_target_price}')
                    order_status = 'Completed'
                    break

            else:
                order_status = api_methods.get_order_status_websocket(buy_limit_order_id)
                time.sleep(0.5)

        if should_exit == False:
            print('Buy Order Completed, Placing Stop Loss')
            stop_loss_order_id = self.trade.stop_loss_sell_order(sl_price,self.trigger_price_factor)  # Fixed function call
            print('Monitoring LTP........')

        order_status = 'Pending'
        while should_exit == False:

            ltp = api_methods.get_ltp_websocket(self.trade.symbol)
            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            order_status = api_methods.get_order_status_websocket(stop_loss_order_id)

            if order_status == 'Completed':
                print('Stop Loss Hit, Exiting from the trade')
                should_exit = True
                break

            elif self.trade.check_condition_to_force_sell(order_status, sl_price,ltp):
                stop_loss_market_order_id = self.trade.modify_to_market_order(stop_loss_order_id,'SELL')
                print(f'Forced Exit From Market as price became @ {ltp}')

                market_sell_price = api_methods.get_order_avg_price(stop_loss_market_order_id)
                while market_sell_price is None:
                    market_sell_price = api_methods.get_order_avg_price(stop_loss_market_order_id)
                    time.sleep(0.5)

                print(f'Market Sell Order Completed @ {market_sell_price}')
                should_exit = True
                break
                
            # elif ltp > sl_target_price * (self.factor + 0.01) + self.trigger_price_factor:
            elif ltp > sl_target_price + self.trigger_price_factor and self.big_move == False:
                print('Increasing Stop Loss to Target Price')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(stop_loss_order_id, sl_target_price)
                print('Stop Loss To Target Modified')
                break

            elif ltp > sl_target_price * (1+self.factor + 0.01) + self.trigger_price_factor and self.big_move == True:
                print('Increasing Stop Loss to Target Price')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(stop_loss_order_id, sl_target_price)
                print('Stop Loss To Target Modified')
                break

            else:
                # print('Waiting')
                time.sleep(0.5)
                continue
                
        if should_exit == False:
            print('Entering Trailing Stop Loss Loop')

        order_status = 'Pending'
        while should_exit == False:

            ltp = api_methods.get_ltp_websocket(self.trade.symbol)
            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            order_status = api_methods.get_order_status_websocket(modify_stop_loss_target_id)

            if order_status == 'Completed':
                print(f'Target Hit, Complete @ {sl_target_price}')
                should_exit = True
                break

            elif order_status != 'Completed' and ltp < sl_target_price:
                stop_loss_market_order_id = self.trade.modify_to_market_order(modify_stop_loss_target_id,'SL-SELL')
                print(f'Forced Target Exit From Market as price became @ {ltp}')

                market_sell_price = api_methods.get_order_avg_price(modify_stop_loss_target_id)
                while market_sell_price is None:
                    market_sell_price = api_methods.get_order_avg_price(modify_stop_loss_target_id)
                    time.sleep(0.5)

                print(f'Market Sell Order Completed @ {market_sell_price}')
                should_exit = True
                break   

            elif ltp > sl_target_price * (1+self.factor + 0.01) + self.trigger_price_factor:
                sl_target_price = api_methods.convert_to_nearest(sl_target_price * self.factor)
                print(f'Increasing Target to @ {sl_target_price}')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(modify_stop_loss_target_id, sl_target_price)
                print(f'Increased Target Price to @ {sl_target_price}')

            else:
                # print('Waiting')
                time.sleep(0.5)
                continue

    
    def sell_trail_stop_loss(self):
        should_exit = False

        print('*********************************Sell And Trail Stop Loss Function Called*********************************')
        sell_price = api_methods.get_ltp_websocket(self.trade.symbol)
        sell_limit_order_id = self.trade.sell_limit_order(sell_price)  # Fixed function call
        sl_price = api_methods.convert_to_nearest(sell_price * (1 + self.sl_percent))
        sl_target_price = api_methods.convert_to_nearest(sell_price * (1 - self.target_percent))
        print(f'Sell Price: {sell_price}, sl_price: {sl_price}, sl_target_price: {sl_target_price}')

        print('Checking Sell Order Status.......')
        order_status = 'Pending'
        while order_status != 'Completed':

            order_status = api_methods.get_order_status_websocket(sell_limit_order_id)
            ltp = api_methods.get_ltp_websocket(self.trade.symbol)

            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            if order_status != 'Completed' and ltp < sell_price * 0.995:
                if not self.forced_entry:
                    print(f'Cancelling Sell Limit Order as Price Became : {ltp}')
                    api_methods.cancel_order(sell_limit_order_id)
                    order_status = 'Completed'
                    should_exit = True
                    break

                if self.forced_entry:
                    print(f'Placing Forced Market Sell Order as LTP Became: {ltp}')
                    sell_market_order_id = self.trade.modify_to_market_order(sell_limit_order_id,'SELL')

                    market_sell_price = api_methods.get_order_avg_price(sell_market_order_id)
                    while market_sell_price is None:
                        market_sell_price = api_methods.get_order_avg_price(sell_market_order_id)
                        time.sleep(0.5)

                    sl_price = api_methods.convert_to_nearest(market_sell_price * (1 + self.sl_percent))
                    sl_target_price = api_methods.convert_to_nearest(market_sell_price * (1 - self.target_percent))
                    sell_limit_order_id = sell_market_order_id
                    print(f'Market Buy Price: {market_sell_price}, sl_price: {sl_price}, sl_target_price: {sl_target_price}')
                    order_status = 'Completed'
                    break

            else:
                order_status = api_methods.get_order_status_websocket(sell_limit_order_id)
                time.sleep(0.5)

        if should_exit == False:
            print('Sell Order Completed, Placing Stop Loss')
            stop_loss_order_id = self.trade.stop_loss_buy_order(sl_price)  # Fixed function call
            print('Monitoring LTP........')

        order_status = 'Pending'
        while should_exit == False:

            ltp = api_methods.get_ltp_websocket(self.trade.symbol)
            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            order_status = api_methods.get_order_status_websocket(stop_loss_order_id)

            if order_status == 'Completed':
                print('Stop Loss Hit, Exiting from the trade')
                should_exit = True
                break

            elif self.trade.check_condition_to_force_buy(order_status, sl_price,ltp):
                stop_loss_market_order_id = self.trade.modify_to_market_order(stop_loss_order_id,'BUY')
                print(f'Forced Exit From Market as price became @ {ltp}')

                market_buy_price = api_methods.get_order_avg_price(stop_loss_market_order_id)
                while market_buy_price is None:
                    market_buy_price = api_methods.get_order_avg_price(stop_loss_market_order_id)
                    time.sleep(0.5)

                print(f'Market Buy Order Completed @ {market_sell_price}')
                should_exit = True
                break
                
            # elif ltp > sl_target_price * (self.factor + 0.01) + self.trigger_price_factor:
            elif ltp < sl_target_price - self.trade.trigger_price_factor and self.big_move == False:
                print('Increasing Stop Loss to Target Price')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(stop_loss_order_id, sl_target_price)
                print('Stop Loss To Target Modified')
                break

            elif ltp < sl_target_price * (1 - self.factor - 0.01) - self.trade.trigger_price_factor and self.big_move == True:
                print('Increasing Stop Loss to Target Price')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(stop_loss_order_id, sl_target_price)
                print('Stop Loss To Target Modified')
                break

            else:
                # print('Waiting')
                time.sleep(0.5)
                continue
                
        if should_exit == False:
            print('Entering Trailing Stop Loss Loop')

        order_status = 'Pending'
        while should_exit == False:

            ltp = api_methods.get_ltp_websocket(self.trade.symbol)
            while ltp is None:
                ltp = api_methods.get_ltp_websocket(self.trade.symbol)
                time.sleep(0.1)

            order_status = api_methods.get_order_status_websocket(modify_stop_loss_target_id)

            if order_status == 'Completed':
                print(f'Target Hit, Complete @ {sl_target_price}')
                should_exit = True
                break

            elif order_status != 'Completed' and ltp < sl_target_price:
                stop_loss_market_order_id = self.trade.modify_to_market_order(modify_stop_loss_target_id,'SL-SELL')
                print(f'Forced Target Exit From Market as price became @ {ltp}')

                market_sell_price = api_methods.get_order_avg_price(modify_stop_loss_target_id)
                while market_sell_price is None:
                    market_sell_price = api_methods.get_order_avg_price(modify_stop_loss_target_id)
                    time.sleep(0.5)

                print(f'Market Sell Order Completed @ {market_sell_price}')
                should_exit = True
                break   

            elif ltp < sl_target_price * (1 - self.factor - 0.01) - self.trade.trigger_price_factor:
                sl_target_price = api_methods.convert_to_nearest(sl_target_price * (1 - self.factor))
                print(f'Increasing Target to @ {sl_target_price}')
                modify_stop_loss_target_id = self.trade.modify_stop_loss_order(modify_stop_loss_target_id, sl_target_price)
                print(f'Increased Target Price to @ {sl_target_price}')

            else:
                # print('Waiting')
                time.sleep(0.5)
                continue
