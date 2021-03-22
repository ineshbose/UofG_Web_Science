import json
import tweepy

from . import processing
from .counter import Counter
from .dataCollector import DataCollector


class StreamListener(tweepy.StreamListener):
    """
    A class provided by tweepy to access the Twitter Streaming API.
    """

    def __init__(self, **kwargs):
        self.collected_tweets_count = 0
        self.collected_tweets = []
        self.collector = DataCollector()
        super().__init__(**kwargs)

    def on_connect(self):
        print("You are now connected to the Streaming API.")

    def on_disconnect(self, notice):
        print("Disconnected to the Streaming API.")

    def on_error(self, status_code):
        print(f"An Error has occured: {repr(status_code)}")

    def on_exception(self, exception):
        self.on_error(exception)

    def on_data(self, data):

        super().on_data(data)
        Counter.total_tweets_count += 1

        t = json.loads(data)
        tweet = processing.processTweet(t)

        if tweet["country_code"] == "GB" or tweet["place_country"] == "United Kingdom":
            Counter.count_collected(tweet)
            self.collected_tweets.append(tweet)
        Counter.display()

        if self.collected_tweets and self.collected_tweets_count % 50 == 0:
            self.collector.add(self.collected_tweets)
            self.collected_tweets = []