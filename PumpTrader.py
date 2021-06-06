from token_profiler.telegram_bot import Telegram
from blockchain.trader import Trader
from time import sleep
import decimal
import numpy as np

class PumpTrader:
    def __init__(self):
        self.trader = Trader()

    def get_address(self, channel):
        #Listen for Telegram message containing contract address
        telegram_bot = Telegram()
        token_address = telegram_bot.listen_for_messages(channel)
        print("Found token: ", token_address)
        return token_address

    def trade_pump(self, token_address, trade_size):
        #BUY
        buy_tx = self.trader.swapExactETHForTokens(token_address,
                                    transferAmountInBNB=trade_size, 
                                    gasPriceGwei=15, 
                                    minutesDeadline=2, 
                                    retries=10,
                                    verbose=True,
                                    actually_send_trade=True)
        assert(not buy_tx == "Failed")

        #Get actual balance recieved from the trade
        shitcoin_balance = self.trader.get_shitcoin_balance(token_address)
        initial_price = np.divide(np.float64(shitcoin_balance) , np.float64(trade_size))

        #Monitor price with trailing stop loss
        sl_ratio = decimal.Decimal(0.85)
        stop_loss = decimal.Decimal(initial_price) * sl_ratio

        print(f"======\nSuccessful Buy! Shitcoin Balance: {shitcoin_balance} @ Price {initial_price}, SL @ {stop_loss}\n=======")

        #Approve the reverse swap
        approval_tx = self.trader.approve_token(token_address)
        assert(not approval_tx == "Failed")
        print("Approval successful!")

        price = initial_price
        while True:
            price = self.trader.get_shitcoin_price_in_bnb(token_address)

            #SELL
            if price <= stop_loss \
                or price >= initial_price*2:
                print(f"Triggering SELL @ {price}")
                sell_tx = self.trader.swapExactTokensForETH(token_address,
                                            gasPriceGwei=15, 
                                            minutesDeadline=2,
                                            max_slippage=49,
                                            retries=10,
                                            verbose=True,
                                            actually_send_trade=True)
                assert(not sell_tx == "Failed")
                break
            #Raise SL barrier each loop
            sl_ratio = decimal.Decimal(min(sl_ratio * decimal.Decimal(1.005), 0.9))
            stop_loss = max(price * sl_ratio, stop_loss)
            
            print(f"======\nPrice: {price}\nStop Loss: {stop_loss}\n---------")
            sleep(2)

        print("Success!")
        print("Final BNB Gwei balance: ", self.trader.get_bnb_balance(convertToBNB=False))

    def record_price(self, token_address, time):
        prices = {}
        for i in range(time):
            prices[str(i)] = self.trader.get_shitcoin_price_in_bnb(token_address)
            sleep(1)
        return prices

    # Monitor the price for the duration of the pump
    def monitor(self, channel, time=120):
        token_address = self.get_address(channel)
        return self.record_price(token_address, time)

    def execute(self, channel, trade_size):
        token_address = self.get_address(channel)
        self.trade_pump(token_address, trade_size)