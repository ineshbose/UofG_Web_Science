import time
import tweepy
import threading

from . import api
from . import processing

from .counter import Counter
from .dataCollector import DataCollector


class TwitterCursor:

    def __init__(self):
        self.api = api
        self.max_id = None
        self.since_id = None
        self.collector = DataCollector()

    def limit_handled(self, cursor, **filters):
        while True:
            try:
                c = cursor(since_id=self.since_id, max_id=self.max_id, **filters)
                self.since_id, self.max_id = (
                    (c[-1].id, c[0].id) if c else (self.since_id, self.max_id)
                )
                yield from c
            except tweepy.RateLimitError:
                print("Search rate reached. Waiting..")
                time.sleep(15 * 60)
            except tweepy.TweepError as e:
                print(f"Something went wrong: {e}")

    def begin(self, **filters):
        for c in self.limit_handled(self.api.search, **filters):
            Counter.total_tweets_count += 1
            tweet = processing.processTweet(c._json)
            if tweet["country_code"] == "GB" or tweet["place_country"] == "United Kingdom":
                Counter.count_collected(tweet)
                self.collector.add(tweet)
        Counter.display()

    def search(self, is_async=False, **filters):
        if is_async:
            threading.Thread(target=self.begin, kwargs=filters).start()
        else:
            self.begin(**filters)