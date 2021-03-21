import time
import tweepy

from src import cursor, filters, streamer
'''

streamer.filter(
    locations=filters.locations, track=filters.words, languages=["en"], is_async=False
)
'''
last_id = None
counter = 0
sinceID = None

results = True
'''
while results:
    #if counter < 180:
    results = api.search(
        geocode=filters.geocode,
        count=100,
        lang="en",
        tweet_mode="extended",
        max_id=last_id,
    )  # , since_id = sinceID)
    print(results)
    counter += 1
'''
l = []
for c in cursor.search(
        geocode=filters.geocode,
        count=100,
        lang="en",
        tweet_mode="extended",
        max_id=last_id,
    ):
    if c.id not in l:
        l.append(c.id)
    else:
        print(c.id)