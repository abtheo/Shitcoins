import token_profiler.reddit_scraper as reddit_scraper
import token_profiler.profiler as profiler
import blockchain.trader as Trading
import pandas as pd
import threading
from datetime import *
# Step 1 - scrape Reddit
# Step 2 - store token ID locally/deduplicate
# Step 3 - get dictionary from bscscan.py (profiler)
# Step 4 - do some logic to figure out how much to buy, choose trading strategy
# Step 5 - monitor price (pikey code from trader.py)
# Step 6 - Use trader.py to buy/sell

# Thread class to track and trade a specific shitcoin contract address
class Shitcoin(threading.Thread):
    def __init__(self, contract, profile):
        threading.Thread.__init__(self)

        # Establish whether pancakeswap v1 or v2 is better
        if profile['v1_bnb_holdings'] > profile['v2_bnb_holdings']:
            self.type = 'v1'
        else: self.type = 'v2'

        stats = profile['stats']

        self.sellExists = profile['sell_exists']

        self.earliest_tx = stats['age']
        self.dateSeen = pd.Timestamp.now(tz=timezone.utc)

    def run(self):
        if not self.sellExists:
            return
        pass

# Class for overseeing the trading of shitcoins, and
class Tracker:
    def __init__(self):
        #self.trader = Trading.Trader()
        self.tokenProfiler = profiler.Profiler()
        self.tokenDict = {}

    def track(self):
        while(True):
            redditTokens = reddit_scraper.scrape_subreddits(time=30)
            addresses = [a for a in redditTokens["address"] if a != '']

            for a in addresses:
                if a not in self.tokenDict.keys():
                    print("============================================")
                    print("Address: " + a)
                    profile = self.tokenProfiler.profile_token(a)
                    print(profile['stats'])
                    self.tokenDict[a] = Shitcoin(a, profile)
                    self.tokenDict[a].run()

            # Converting to Dictionary removes duplicates and allows contextualising
            self.tokenDict = dict.fromkeys(addresses)
            print(tokenDict)
            time.wait(20)

        #print("Profiling MoonCunt:")
        #print(self.tokenProfiler.profile_token('0x5bf5a3c97dd86064a6b97432b04ddb5ffcf98331'))

t = Tracker()
t.track()
