import token_profiler.reddit_scraper as reddit_scraper
import token_profiler.profiler as profiler
import blockchain.trader as Trading
import pandas as pd
import threading
# Step 1 - scrape Reddit
# Step 2 - store token ID locally/deduplicate
# Step 3 - get dictionary from bscscan.py (profiler)
# Step 4 - do some logic to figure out how much to buy, choose trading strategy
# Step 5 - monitor price (pikey code from trader.py)
# Step 6 - Use trader.py to buy/sell

# Thread class to discover new shitcoin contract addresses
class Discovery (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self, dataFrame):
        while(true):
            time.sleep(20)
            newTokens = reddit_scraper.scrape_subreddits(time=30)
            # TODO: Lock 'dataFrame'
            dataFrame.merge(newTokens, how='outer')

# Thread class to track and trade a specific shitcoin contract address
class Shitcoin(threading.Thread):
    def __init__(self, contract, trader):
        threading.Thread.__init__(self)

# Class for overseeing the trading of shitcoins, and
class Tracker:
    def __init__(self):
        self.tokens = reddit_scraper.scrape_subreddits(time=1000)
        self.trader = Trading.Trader()
        print(self.tokens["address"])

        # TODO - keep searching and deduplicate
        #newTokens = reddit_scraper.scrape_subreddits()
        #dataFrame.merge(newTokens, how='outer', )
        for index, row in self.tokens.iterrows():
            print(index)

tokenProfiler = profiler.Profiler()
