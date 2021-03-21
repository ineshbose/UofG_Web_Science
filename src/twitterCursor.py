import time
import tweepy
from . import api


class TwitterCursor:
    def __init__(self):
        self.api = api

    def limit_handled(self, cursor, **kwargs):
        while True:
            print("hmm")
            try:
                yield from cursor(**kwargs)
            except tweepy.RateLimitError:
                print("cool")
                #time.sleep(15 * 60)

    def search(self, **kwargs):
        return self.limit_handled(self.api.search, **kwargs)