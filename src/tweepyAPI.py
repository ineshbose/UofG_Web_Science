import time
import tweepy
from . import api


class TweepyAPI(tweepy.API):
    def __init__(self):
        self.api = api

    def search(self, **kwargs):
        while True:
            try:
                super().search(**kwargs)
            except tweepy.RateLimitError:
                time.sleep(15 * 60)
