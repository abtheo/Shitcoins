from PumpTrader import PumpTrader

# Monitor the specified channel and buy announced tokens with a position size of 0.075 BNB
pump_trader = PumpTrader()
pump_trader.execute("t.me/bscpumpingrocket", 0.075)
