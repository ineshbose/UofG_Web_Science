import re
import json
import emoji
from tweepy import StreamListener
from datetime import datetime

from . import db, collection


class StreamListener(StreamListener):
    """
    A class provided by tweepy to access the Twitter Streaming API.
    """

    def __init__(self, **kwargs):
        self.total_tweets = 0
        self.collected_tweets = 0
        super().__init__(**kwargs)

    def on_connect(self):
        collection.drop()
        print("You are now connected to the Streaming API.")

    def on_error(self, status_code):
        print(f"An Error has occured: {repr(status_code)}")

    def on_exception(self, exception):
        self.on_error(exception)

    def on_disconnect(self, notice):
        print(
            "Disconnected to the Streaming API.",
            f"Total tweets: {self.total_tweets}",
            f"Collected tweets: {self.collected_tweets}",
            sep="\n"
        )

    def strip_emoji(self, text):
        return re.sub(emoji.get_emoji_regexp(), r"", text)

    def cleanList(self, text):
        text = self.strip_emoji(text)
        text.encode("ascii", errors="ignore").decode()
        return text

    def processTweets(self, tweet):

        created = datetime.strptime(
            tweet.get("created_at", "Thu Jan 01 00:00:00 +0000 1970"), "%a %b %d %H:%M:%S +0000 %Y"
        )

        tweet_id = tweet.get("id_str")
        username = tweet["user"].get("screen_name") if "user" in tweet else None

        text = self.cleanList(
            tweet["extended_tweet"]["full_text"] if tweet.get("truncated")
            else ((
                tweet["retweeted_status"]["extended_tweet"]["full_text"]
                if tweet["retweeted_status"].get("truncated")
                else tweet["retweeted_status"].get(
                    "full_text", tweet["retweeted_status"]["text"]
                )) if tweet.get("text", "").startswith("RT") and "retweeted_status" in tweet else tweet.get("text", "")
            )
        )

        quote_count = tweet.get("quote_count")
        reply_count = tweet.get("reply_count")
        retweet_count = tweet.get("retweet_count")
        favorite_count = tweet.get("favorite_count")

        entities = tweet.get("entities") if not tweet.get("truncated") else tweet["extended_tweet"].get("entities")
        mList = [x["screen_name"] for x in entities.get("user_mentions", [])] if entities else []
        hList = [x["text"] for x in entities.get("hashtags", [])] if entities else []
        mediaList = [{"type":x.get("type"), "link":x.get("media_url")} for x in entities.get("media", [])] if entities else []
        source = tweet.get("source")

        exactcoord = tweet.get("coordinates")
        coordinates = exactcoord.get("coordinates") if exactcoord else None
        geoenabled = tweet["user"].get("geo_enabled", False) if "user" in tweet else False
        location = tweet["user"].get("location") if "user" in tweet else None

        place_name, place_country, place_countrycode, place_coordinates = (
            tweet["place"].get("full_name"), tweet["place"].get("country"), tweet["place"].get("country_code"), tweet["place"].get("bounding_box", {"coordinates": []})["coordinates"]
        ) if geoenabled and not text.startswith("RT") and tweet.get("place") else (None, None, None, None)

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
            "media": mediaList,
            "source": source,
            "quotes": quote_count,
            "replies": reply_count,
            "retweets": retweet_count,
            "favorites": favorite_count,
        }

    def on_data(self, data):

        super().on_data(data)
        self.total_tweets += 1

        t = json.loads(data)
        tweet = self.processTweets(t)

        if tweet["place_country"] == "United Kingdom":
            self.collected_tweets += 1
            collection.insert_one(tweet)