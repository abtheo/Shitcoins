from token_profiler.telegram_bot import Telegram
from blockchain.trader import Trader
from time import sleep
import decimal
import numpy as np

#Listen for Telegram message containing contract address
telegram_bot = Telegram()
token_address = telegram_bot.listen_for_messages("t.me/bscpumpingrocket")
print("Found token: ", token_address)

#Position size in BNB
trade_size = 0.075

trader = Trader()
#BUY
buy_tx = trader.swapExactETHForTokens(token_address,
                            transferAmountInBNB=trade_size, 
                            gasPriceGwei=15, 
                            minutesDeadline=2, 
                            retries=10,
                            verbose=True,
                            actually_send_trade=True)
assert(not buy_tx == "Failed")

# #Get actual balance recieved from the trade
shitcoin_balance = trader.get_shitcoin_balance(token_address)
initial_price = np.divide(np.float64(shitcoin_balance) , np.float64(trade_size))

#Monitor price with trailing stop loss
sl_ratio = decimal.Decimal(0.85)
stop_loss = decimal.Decimal(initial_price) * sl_ratio

print(f"======\nSuccessful Buy! Shitcoin Balance: {shitcoin_balance} @ Price {initial_price}, SL @ {stop_loss}\n=======")

#Approve the reverse swap
approval_tx = trader.approve_token(token_address)
assert(not approval_tx == "Failed")
print("Approval successful!")

price = initial_price
while True:
    price = trader.get_shitcoin_price_in_bnb(token_address)

    #SELL
    if price <= stop_loss \
        or price >= initial_price*2:
        print(f"Triggering SELL @ {price}")
        sell_tx = trader.swapExactTokensForETH(token_address,
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
print("Final BNB Gwei balance: ", trader.get_bnb_balance(convertToBNB=False))
