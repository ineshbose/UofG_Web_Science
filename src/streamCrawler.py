import re
import json
import emoji
import tweepy
from datetime import datetime

from . import collection


class StreamListener(tweepy.StreamListener):
    """
    A class provided by tweepy to access the Twitter Streaming API.
    """

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        print(f"An Error has occured: {repr(status_code)}")

    def strip_emoji(self, text):
        return re.sub(emoji.get_emoji_regexp(), r"", text)

    def cleanList(self, text):
        text = self.strip_emoji(text)
        text.encode("ascii", errors="ignore").decode()
        return text

    def processTweets(self, tweet):
        place_countrycode = None
        place_name = None
        place_country = None
        place_coordinates = None
        exactcoord = None
        place = None

        created = datetime.strptime(tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y")
        tweet_id = tweet["id_str"]
        username = tweet["user"]["screen_name"]
        text = tweet["text"]

        if tweet.get("truncated"):
            text = tweet["extended_tweet"]["full_text"]
        elif text.startswith("RT"):
            text = (
                tweet["retweeted_status"]["extended_tweet"]["full_text"]
                if tweet["retweeted_status"]["truncated"]
                else tweet["retweeted_status"].get(
                    "full_text", tweet["retweeted_status"]["text"]
                )
            )

        text = self.cleanList(text)

        mList = [x["screen_name"] for x in tweet["entities"]["user_mentions"]]
        hList = [x["text"] for x in tweet["entities"]["hashtags"]]
        source = tweet["source"]

        exactcoord = tweet["coordinates"]
        coordinates = exactcoord["coordinates"] if exactcoord else None
        geoenabled = tweet["user"]["geo_enabled"]
        location = tweet["user"]["location"]

        if (geoenabled) and not text.startswith("RT"):
            if tweet.get("place"):
                place_name = tweet["place"]["full_name"]
                place_country = tweet["place"]["country"]
                place_countrycode = tweet["place"]["country_code"]
                place_coordinates = tweet["place"]["bounding_box"]["coordinates"]

        return {
            "_id": tweet_id,
            "date": created,
            "username": username,
            "text": text,
            "geoenabled": geoenabled,
            "coordinates": coordinates,
            "location": location,
            "place_name": place_name,
            "place_country": place_country,
            "country_code": place_countrycode,
            "place_coordinates": place_coordinates,
            "hashtags": hList,
            "mentions": mList,
            "source": source,
        }

    def on_data(self, data):
        t = json.loads(data)
        tweet = self.processTweets(t)
        if tweet["geoenabled"]:
            collection.insert_one(tweet)
