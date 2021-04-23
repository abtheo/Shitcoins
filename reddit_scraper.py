import numpy as np
import pandas as pd
import datetime as dt
import requests
import json
from datetime import date
from dateutil.rrule import rrule, DAILY
from queue import Queue
import re


def extract_selftext_info(selftext):
    url_pattern = "(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,}\b([-a-zA-Z0-9@:%_\+.~#?&\/#\/=]*)"
    re.findall("(?P<url>https?://[^\s]+)", selftext)

    # print(matches)

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


def try_get(d, idx):
    try:
        return d[idx]
    except:
        return np.nan

def parse_json_fields(request):
    # "subreddit": try_get(data, "subreddit"),
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
        "total_awards_received": try_get(data, "total_awards_received")
    } for data in request]


url = r"https://api.pushshift.io/reddit/submission/search/?" + \
    r"&sort_type=score" + \
    r"&after=240s" + \
    r"&sort=desc" + \
    r"&size=5" 

subreddits = ["CryptoMoonshots"]

tracked_tokens = UniqueQueue(maxsize=10)

#SEARCH Loop - Query for new posts
for sub in subreddits:
    #Send request to subreddit
    sub_url = url + f"&subreddit={sub}"
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

    for i in range(len(df)):
        print(df["selftext"].iloc[i])
        #Extract relevant info from selftext
        extract_selftext_info(df["selftext"].iloc[i])

    #Check if the asset is already blacklisted

    #Add link as ID to stack
    # post_queue.queue(df["full_link"])



# ['full_link', 'created_utc', 'title', 'score', 'num_comments',
#        'num_crossposts']