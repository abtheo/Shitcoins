from token_profiler.telegram_bot import Telegram
from blockchain.trader import Trader
from time import sleep
import decimal
import numpy as np

#Listen for Telegram message containing contract address
telegram_bot = Telegram()
token_address = telegram_bot.listen_for_messages("t.me/testchannelignoreme")
print("Found token: ", token_address)

#Position size in BNB
trade_size = np.float32(0.01)

#BUY
trader = Trader()
buy_tx = trader.swapExactETHForTokens(token_address,
                            transferAmountInBNB=trade_size, 
                            gasPriceGwei=8, 
                            minutesDeadline=1, 
                            retries=5,
                            verbose=True,
                            actually_send_trade=True)
assert(not buy_tx == "Failed")

# #Get actual balance recieved from the trade
shitcoin_balance = trader.get_shitcoin_balance(token_address)
initial_price = np.divide(np.float64(shitcoin_balance) , trade_size)
print(f"Successful Buy! Shitcoin Balance: {shitcoin_balance} @ Price {initial_price}")

#Monitor price with trailing stop loss
sl_ratio = decimal.Decimal(0.995)
stop_loss = decimal.Decimal(initial_price) * sl_ratio

#Approve the reverse swap
approval_tx = trader.approve_token(token_address)
assert(not approval_tx == "Failed")


price = initial_price
while True:
    print(f"======\nPrice: {price}\nStop Loss: {stop_loss}\n---------")
    price = trader.get_shitcoin_price_in_bnb(token_address)

    #SELL
    if price <= stop_loss \
        or price >= initial_price*2:
        
        sell_tx = trader.swapExactTokensForETH(token_address,
                                    gasPriceGwei=8, 
                                    minutesDeadline=1,
                                    retries=10,
                                    verbose=True,
                                    actually_send_trade=True)
        assert(not sell_tx == "Failed")
        break
    stop_loss = max(price * sl_ratio, stop_loss)
    sleep(3)

print("Success!")