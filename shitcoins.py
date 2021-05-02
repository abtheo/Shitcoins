import token_profiler.reddit_scraper as reddit_scraper
import token_profiler.profiler as profiler
import blockchain.trader as Trading
import pandas as pd
import threading
from datetime import datetime, timedelta
# Step 4 - do some logic to figure out how much to buy, choose trading strategy
# Step 5 - monitor price (pikey code from trader.py)
# Step 6 - Use trader.py to buy/sell

# Thread class to track and trade a specific shitcoin contract address
class Shitcoin(threading.Thread):
    def __init__(self, contract, profile, bnb, trader):
        threading.Thread.__init__(self)

        # Establish whether pancakeswap v1 or v2 is better
        if profile['v1_bnb_holdings'] > profile['v2_bnb_holdings']:
            self.type = 'v1'
        else: self.type = 'v2'

        stats = profile['stats']
        self.contract = contract
        self.sellExists = profile['sell_exists']
        self.trader = trader
        self.earliest_tx = stats['age'].to_pydatetime()
        self.dateSeen = datetime.now()
        self.bnb = bnb

    def currentPrice(self):
        self.trader.getCurrentPrice(self.contract)

    def printBalance(self):
        print(self.contract + ": You have " + self.bnb + " BNB and " + self.shitcoin + " tokens.")

    def buy(self, bnb):
        self.bnb -= bnb
        self.shitcoin += bnb / currentPrice()
        print(self.contract + ": Bought " + self.shitcoin + " for " + currentPrice())


    def sell(self, shitcoin):
        self.shitcoin -= shitcoin
        self.bnb += shitcoin * currentPrice()
        print(self.contract + ": Sold " + self.shitcoin + " for " + currentPrice())

    def earlyEntryStrategy(self):
        entryPrice = currentPrice()
        buy(min(0.05, bnb))
        while (True):
            price = currentPrice()
            if (price < 0.6 * entryPrice) or (price > 3  * entryPrice):
                break
        sell(self.shitcoin)
        printBalance()

    def run(self):
        if not self.sellExists:
            return
        if (self.dateSeen - self.earliest_tx) > timedelta(hours=1):
            return
        earlyEntryStrategy()

# Class for overseeing the trading of shitcoins, and
class Tracker:
    def __init__(self):
        self.trader = Trading.Trader()
        self.tokenProfiler = profiler.Profiler()
        self.tokenDict = {}

    def track(self):
        while(True):
            redditTokens = reddit_scraper.scrape_subreddits(time=10)
            addresses = [a for a in redditTokens["address"] if a != '']

            for a in addresses:
                if a not in self.tokenDict.keys():
                    print("============================================")
                    print("Address: " + a)
                    profile = self.tokenProfiler.profile_token(a)
                    print(profile['stats'])
                    self.tokenDict[a] = Shitcoin(a, profile, 0.1, self.trader)
                    self.tokenDict[a].run()

            time.wait(10)

        #print("Profiling MoonCunt:")
        #print(self.tokenProfiler.profile_token('0x5bf5a3c97dd86064a6b97432b04ddb5ffcf98331'))

t = Tracker()
t.track()
