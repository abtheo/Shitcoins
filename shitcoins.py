import token_profiler.reddit_scraper as reddit_scraper
import token_profiler.profiler as profiler
import blockchain.trader as Trading
import pandas as pd
import threading
from datetime import datetime, timedelta
import time
# Step 4 - do some logic to figure out how much to buy, choose trading strategy
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
        self.token_sniffer = profile['token_sniffer']

    def currentPrice(self):
        self.trader.get_shitcoin_price_in_bnb(self.contract)

    def printBalance(self):
        print(self.contract + ": You have " + self.bnb + " BNB and " + self.shitcoin + " tokens.")

    # 'Paper' buy
    def buy(self, bnb):
        self.bnb -= bnb
        self.shitcoin += bnb / currentPrice()
        print(self.contract + ": Bought " + self.shitcoin + " for " + currentPrice())

    # 'Paper' sell
    def sell(self, shitcoin):
        self.shitcoin -= shitcoin
        self.bnb += shitcoin * currentPrice()
        print(self.contract + ": Sold " + self.shitcoin + " for " + currentPrice())

    def rugcheck(self):
        if not self.sellExists:
            return 1
        if self.token_sniffer == "SCAM":
            return 1
        if self.token_sniffer == "OKAY":
            return 0
        if self.token_sniffer == "404":
            return 0.5
        # TODO: LP distribution
        # LP distirbution

    def earlyEntryStrategy(self):
        entryPrice = currentPrice()
        peakPrice = entryPrice
        targetMultiplier = 2
        lastTarget = entryPrice
        buy(min(0.05, bnb))

        while (True):
            price = currentPrice()
            peakPrice = max(price, peakPrice)

            # If it drops 40% from the all-time high, sell all
            if (price < 0.6 * peakPrice):
                sell(self.shitcoin)
                return

            # Sell 25% of holdings each time price goes up by another multiple
            if (price > lastTarget * targetMultiplier):
                sell(0.25*self.shitcoin)
                lastTarget = lastTarget * targetMultiplier
            time.sleep(2)

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

    def track(self, trading_mode=True):
        while(True):
            redditTokens = reddit_scraper.scrape_subreddits(time="11000s")
            print(redditTokens)
            try:
                addresses = [a for a in redditTokens["address"] if a != '']
            except:
                addresses = []

            for a in addresses:
                if a not in self.tokenDict.keys():
                    print("============================================")
                    print("New Token Discovered: " + a)
                    print("Time: " + str(datetime.now()))

                    if (trading_mode):
                        profile = self.tokenProfiler.profile_token(a)
                        #print("Profile:")
                        #print(profile)
                        self.tokenDict[a] = Shitcoin(a, profile, 0.1, self.trader)
                        self.tokenDict[a].run()

            time.sleep(10)

        #print("Profiling MoonCunt:")
        #print(self.tokenProfiler.profile_token('0x5bf5a3c97dd86064a6b97432b04ddb5ffcf98331'))

t = Tracker()
t.track(trading_mode = True)

#print(reddit_scraper.scrape_subreddits(time='11000s', subreddits=['cryptomoonshots']))
