import token_profiler.reddit_scraper as reddit_scraper
from token_profiler.profiler import Profiler
from token_profiler.ape_scraper import ApeScraper
from blockchain.trader import Trader
import pandas as pd
import threading
from datetime import datetime, timedelta
import time
import sys
# Step 4 - do some logic to figure out how much to buy, choose trading strategy
# Step 6 - Use trader.py to buy/sell

# Thread class to track and trade a specific shitcoin address address
class Shitcoin(threading.Thread):
    def __init__(self, address, profile, bnb, trader):
        threading.Thread.__init__(self)

        # Establish whether pancakeswap v1 or v2 is better
        if profile['v1_bnb_holdings'] > profile['v2_bnb_holdings']:
            self.type = 'v1'
        else: self.type = 'v2'

        self.profile = profile
        stats = profile['stats']
        self.address = address
        self.sellExists = profile['sell_exists']
        self.trader = trader
        self.earliest_tx = stats['age'].to_pydatetime()
        self.dateSeen = datetime.now()
        self.bnb = bnb
        self.token_sniffer = profile['token_sniffer']

    def currentPrice(self):
        return self.trader.get_shitcoin_price_in_bnb(self.address)

    def printBalance(self):
        print(self.address + ": You have " + self.bnb + " BNB and " + self.shitcoin + " tokens.")

    # 'Paper' buy
    def buy(self, bnb):
        self.bnb -= bnb
        self.shitcoin += (bnb / self.currentPrice()) * 0.95
        print(self.address + ": Bought " + self.shitcoin + " for " + self.currentPrice())

    # 'Paper' sell
    def sell(self, shitcoin):
        self.shitcoin -= shitcoin
        self.bnb += (shitcoin * self.currentPrice()) * 0.95
        print(self.address + ": Sold " + self.shitcoin + " for " + self.currentPrice())

    # Returns value between 0 and 1, where 0 is definitely safe and 1 is definitely a rugpull
    def rugcheck(self):
        rugstatus = 1

        # Almost certainly a rugpull:
        if (not self.sellExists) or (self.token_sniffer == "SCAM"):
            return 1

        # If Token Sniffer says it's OK, then unlikely to be rug.
        # If 404, then very new coin and fairly likely to rug.
        if self.token_sniffer == "OKAY":
            rugstatus *= 0.25
        elif self.token_sniffer == "404":
            rugstatus *= 0.75

        # If not much liquidity is locked, then reasonable chance it's a rugpull
        if self.profile["locked_liquidity"] < 1.5:
            rugstatus *= 0.5

        return rugstatus
        # TODO: LP distribution
        # LP distirbution

    # This trading strategy is applied to coins that are being targeted by a
    # 'pump-and-dump' campaign. It buys in, and only sells out when there is
    # indication that the price is beginning to fall.
    def pumpDumpStrategy(self, amount):
        entryPrice = self.currentPrice()
        peakPrice = entryPrice
        lastTarget = entryPrice
        buy(min(amount, bnb)) # TODO

        while (True):
            price = self.currentPrice()
            peakPrice = max(price, peakPrice)

            # If it drops 20% from the all-time high, sell all.
            # This could potentially be optimised - e.g. factoring in the number
            # of sell orders or whether a dip is being quickly eaten up.
            if (price < 0.8 * peakPrice):
                sell(self.shitcoin)
                return

            time.sleep(0.2)

    def earlyEntryStrategy(self):
        if self.rugcheck() < 0.5:
            print("Rugpull...")
            return
        print("==========FOUND A MOONSHOT==========")
        print(self)
        print("================================")
        entryPrice = self.currentPrice()
        peakPrice = entryPrice
        targetMultiplier = 1.5
        lastTarget = entryPrice
        buy(min(0.05, bnb))

        while (True):
            price = self.currentPrice()
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

    def run(self, type):
        print(self.profile)
        #Ensure Locked Liquidity >= BNB
        if self.profile["locked_liquidity"] < 1.5:
            return
        #Ensure at least one Sell transaction has happened
        if not self.profile["sell_exists"]:
            return
        #Less than X hours old
        if (self.dateSeen - self.earliest_tx) > timedelta(hours=4):
            return

        print("MOONSHOT")
        # self.earlyEntryStrategy()


# Class for overseeing the trading of shitcoins, and
class Tracker:
    def __init__(self):
        self.trader = Trader()
        self.tokenProfiler = Profiler()
        self.tokenDict = {}
        self.ape_scraper = ApeScraper(wait_for_table_load_now=True)

    def track(self, refresh_rate=260, trading_mode=True):
        while(True):
            print("\nScraping tokens...")
            # tokens = reddit_scraper.scrape_subreddits(time=f"{int(refresh_rate*2)}s")
            tokens = self.ape_scraper.scrape_ape()
            try:
                addresses = [a for a in tokens["address"] if a != '']
            except:
                addresses = []
            #Start with oldest token and work towards future
            for a in addresses[::-1]:
                a = str(a)
                if a not in self.tokenDict.keys():
                    print("============================================")
                    print("New Token Discovered: ", a)
                    print("Time: " + str(datetime.now()))

                    if (trading_mode):
                        profile = self.tokenProfiler.profile_token(a)
                        #print("Profile:")
                        #print(profile)
                        self.tokenDict[a] = Shitcoin(a, profile, 0.1, self.trader)
                        self.tokenDict[a].run()

            print(f"Sleeping for {refresh_rate}...")
            for i in reversed(range(1, refresh_rate)):
                time.sleep(1 - time.time() % 1) # sleep until a whole second boundary
                sys.stderr.write('\r%4d' % i)
            sys.stderr.write('')


t = Tracker()
t.track(trading_mode = True)
