from token_profiler.telegram_bot import Telegram
from blockchain.trader import Trader
from time import sleep
import decimal


#Listen for Telegram message containing contract address
telegram_bot = Telegram()
token_address = telegram_bot.listen_for_messages("t.me/testchannelignoreme")
print("Found token: ", token_address)

#BUY
trader = Trader()
buy_tx = trader.swapExactETHForTokens(token_address,
                            transferAmountInBNB=0.01, 
                            gasPriceGwei=5, 
                            max_slippage=49, 
                            minutesDeadline=1, 
                            retries=5,
                            verbose=True,
                            actually_send_trade=True)
assert(not buy_tx == "Failed")

#Approve the reverse swap
trader.approve_token(token_address)


#Monitor price with trailing stop loss
price = trader.get_shitcoin_price_in_bnb(token_address)
sl_ratio = decimal.Decimal(0.95)
stop_loss = price * sl_ratio

while True:
    price = trader.get_shitcoin_price_in_bnb(token_address)
    print(f"======\nPrice: {price}\nStop Loss: {stop_loss}\n---------")
    if price <= stop_loss:
        #SELL
        sell_tx = trader.swapExactTokensForETH(token_address,
                                    gasPriceGwei=5, 
                                    max_slippage=49, 
                                    minutesDeadline=1,
                                    retries=10,
                                    verbose=True,
                                    actually_send_trade=True)
        assert(not sell_tx == "Failed")
        break

    stop_loss = max(price * sl_ratio, stop_loss)
    sleep(1)

print("Success!")