import time
import tweepy

from src import api, auth, filters
from src.streamCrawler import StreamListener

listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)
streamer.filter(
    locations=filters.locations, track=filters.words, languages=["en"], is_async=False
)

last_id = None
counter = 0
sinceID = None

results = False

while results:
    if counter < 1:
        results = api.search(
            geocode=filters.geocode,
            count=100,
            lang="en",
            tweet_mode="extended",
            max_id=last_id,
        )  # , since_id = sinceID)
        #print(results)
        counter += 1
    '''
    else:
        time.sleep(15 * 60)
    '''
