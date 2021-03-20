import os
import sys

import tweepy
from pymongo import MongoClient


# Keys, Tokens, Credentials as Environment Variables or Default Values
CONSUMER_KEY = os.environ.get("CONSUMER_KEY", "default")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET", "default")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN", "default")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET", "default")
MONGO_TOKEN = os.environ.get("MONGO_TOKEN", "127.0.0.1")


# Tweepy Setup
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
if not api.verify_credentials():
    sys.exit("Unable to authenticate. Check keys.")


# MongoDB Setup
client = MongoClient(MONGO_TOKEN, 27017)


from .streamCrawler import StreamListener

# Streamer Setup
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)
