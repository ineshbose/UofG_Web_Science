import tweepy
from src import api, auth, filters

d = {f: 0 for f in filters.words}

for i in api.search(q="glasgow"):
    t = i.text
    for w in t.split():
        if w in d:
            d[w] += 1

print(d)
