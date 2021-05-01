from blockchain.trader import Trader
from token_profiler.reddit_scraper import scrape_subreddits
from token_profiler.poocoin import query_poocoin

df = query_poocoin()
print(df)
