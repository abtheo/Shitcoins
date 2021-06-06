from PumpTrader import PumpTrader
import csv
import datetime

shitcoinAddress = "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82"
pump_trader = PumpTrader()
prices = pump_trader.monitor("t.me/bscpumpingrocket", 60)
#prices = pump_trader.record_price(shitcoinAddress, 20)

filename = shitcoinAddress + " - " + str(datetime.date.today()) + ".csv"
with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['Time', 'Price in BNB']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for key, value in prices.items():
        writer.writerow({"Time": key, "Price in BNB": value})