import numpy as np
import pandas as pd
import datetime as dt
import requests
import json
from datetime import date
from dateutil.rrule import rrule, DAILY
from queue import Queue
import re

def fix_shitty_regex(url, query="]("):
    if type(url) == bool:
        return url
    if query not in url:
        return url
    
    idx = word_end_index(url, query)
    return url[:idx].strip(")").strip("]")

def address_from_url(url, end_word):
    try:
        idx = word_end_index(url, end_word)+1
        return url[idx:idx+42]
    except:
        return ""

def word_end_index(text, word):
    wi = wl = len(word)
    for ti, tc in enumerate(text):
        wi = wi - 1 if tc == word[-wi] else wl
        if not wi:
            return ti
    return -1

def try_find_in_matches(query, matches):
    for match in matches:
        if query in match:
            return fix_shitty_regex(match)
    return ""

def extract_selftext_info(selftext):
    """Extract relevant information
    from a Reddit main post.

    Args:
        selftext [str]: 
            Text body of a Reddit post
    """

    #Construct output dict
    social_sites = ["discord", "twitter", "instagram", "youtube","medium", "t.me", "whitepaper", "bscscan_count"]
    df = {}

    #Query post for URLs
    url_pattern = "(?P<url>https?://[^\s]+)"
    url_matches = re.findall(url_pattern, selftext)

    #Query poocoin/pancakeswap and extract token address
    poocoin = try_find_in_matches("poocoin",url_matches)
    pancake = try_find_in_matches("pancakeswap",url_matches)
    
    #Garbage, no need to pursue
    if not (poocoin or pancake):
        return False

    #Extract token address from poo/pancake
    pancake_address = address_from_url(pancake,"outputCurrency=")
    poocoin_address = address_from_url(poocoin,"tokens/")

    if len(pancake_address) == 42:
        df["address"] = pancake_address

    if len(poocoin_address) == 42:
        df["address"] = poocoin_address

    df["poocoin"] = fix_shitty_regex(poocoin)
    df["pancakeswap"] = fix_shitty_regex(pancake)

    #Check for socials
    for site in social_sites:
        df[site] = try_find_in_matches(site,url_matches)

    #Check number of BSCScan URLS linked
    df["bscscan_count"] = sum([1 if "bscscan" in url else 0 for url in url_matches])

    return df

class UniqueQueue(Queue):
    def _init(self, maxsize):
        self.all_items = set()
        Queue._init(self, maxsize)

    def _put(self, item):
        if item not in self.all_items:
            self.all_items.add(item)
            Queue.put(self, item)

    def _get(self):
        item = Queue._get(self)
        self.all_items.remove(item)
        return item

    def queue(self, arr):
        for a in arr:
            self._put(a)
    
    def contains(self, other):
        return other in self.all_items


def try_get(d, idx):
    try:
        return d[idx]
    except:
        return np.nan

def update_row_with_dict(df,d,idx):
    for key in d.keys():
        df.loc[idx, key] = d.get(key)

def parse_json_fields(request):
    return [{
        "id": try_get(data, "id"),
        "full_link": try_get(data, "full_link"),
        "created_utc": try_get(data, "created_utc"),
        "title": try_get(data, "title"),
        "selftext": try_get(data, "selftext"),
        "score": try_get(data, "score"),
        "num_comments": try_get(data, "num_comments"),
        "num_crossposts": try_get(data, "num_crossposts"),
        "upvote_ratio": try_get(data, "upvote_ratio"),
        "total_awards_received": try_get(data, "total_awards_received"),
        "subreddit": try_get(data, "subreddit")
    } for data in request]

def scrape_subreddits():
    url = r"https://api.pushshift.io/reddit/submission/search/?" + \
        r"&sort_type=score" + \
        r"&after=500s" + \
        r"&sort=desc" + \
        r"&size=15" 

    subreddits = ["CryptoMoonshots", "CryptoMarsShots", "AllCryptoBets","Cryptostreetbets",
                "cryptomooncalls","Cryptopumping"]

    token_whitelist = UniqueQueue(maxsize=10)
    token_blacklist = UniqueQueue(maxsize=50)

    #SEARCH Loop - Query for new posts
    for sub in subreddits:
        #Send request to subreddit
        sub_url = url + f"&subreddit={sub}"
        print(f"Sending request to {sub_url}")
        r = requests.get(sub_url)
        if r.status_code != requests.codes.ok:
            print(f"Bad request, skipping {sub_url}")
            continue
        #Parse response as JSON
        j_data = json.loads(r.text)
        data = parse_json_fields(j_data["data"])

        #Drop empty data
        df = pd.DataFrame(data)
        df.dropna(how='all',axis=1,inplace=True)
        if len(df) == 0: 
            print(f"No results found for query {sub_url}")
            continue

        #Add columns for data extraction
        selftext_features = ["poocoin", "pancakeswap", "discord", "twitter", 
            "instagram", "youtube","medium", "t.me", "whitepaper", "bscscan_count"]
        for col in selftext_features:
            df[col] = ""

        #Iterate each post
        for post in range(len(df)):
            selftext = str(df["selftext"].iloc[post])
            #Skip removed posts
            if selftext == "[removed]":
                continue

            #Extract relevant info from selftext
            token_info = extract_selftext_info(selftext)

            #Check if the address is already white/black-listed
            if token_blacklist.contains(token_info["address"]) or token_whitelist.contains(token_info["address"]):
                continue

            #Send Token Address over to Poocoin Scanner
            #Verify integrity of coin
            #Place into whitelist or blacklist
            legit_coin = True
            token_whitelist.put(token_info["address"]) if legit_coin else token_blacklist.put(token_info["address"])
            
            #Merge / Flatten extracted info back into Reddit df
            update_row_with_dict(df,token_info,post)
            

