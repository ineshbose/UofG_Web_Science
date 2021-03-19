import re
import sys
import json
import emoji
from tweepy import StreamListener
from datetime import datetime

from . import db, collection ###
from .dataAnalyser import DataAnalyser
from .dataCollector import DataCollector


class StreamListener(StreamListener):
    """
    A class provided by tweepy to access the Twitter Streaming API.
    """

    def __init__(self, **kwargs):
        self.total_tweets_count = 0
        self.collected_tweets_count = 0
        self.media_count = {}
        self.analyser = DataAnalyser()
        self.collector = DataCollector()
        super().__init__(**kwargs)

    def on_connect(self):
        print("You are now connected to the Streaming API.")

    def on_error(self, status_code):
        print(f"An Error has occured: {repr(status_code)}")

    def on_exception(self, exception):
        self.on_error(exception)

    def on_disconnect(self, notice):
        print(
            "Disconnected to the Streaming API.",
            f"Total tweets: {self.total_tweets_count}",
            f"Collected tweets: {len(self.collected_tweets)}",
            sep="\n",
        )

    def strip_emoji(self, text):
        return re.sub(emoji.get_emoji_regexp(), r"", text)

    def cleanList(self, text):
        text = self.strip_emoji(" ".join(filter(
            lambda x:x[:4]!='http', # and x[0] not in ['@', '#'],
            text.split(),
        )).lower())
        text.encode("ascii", errors="ignore").decode()
        return re.sub(r'[^A-Za-z0-9 ]+', '', text)

    def processTweets(self, tweet):

        curr_time = datetime.now()
        dt_format = "%a %b %d %H:%M:%S +0000 %Y"
        created = datetime.strptime(
            tweet.get("created_at", curr_time.strftime(dt_format)), dt_format
        )
        tweet_id = tweet.get("id_str")
        retweeted = tweet.get("text", "").startswith("RT") and "retweeted_status" in tweet
        quoted = tweet.get("is_quote_status") and "quoted_status" in tweet

        username, description, verified, followers, account_age, defaults = (
            (
                tweet["user"].get("screen_name"),
                tweet["user"].get("description"),
                tweet["user"].get("verified"),
                tweet["user"].get("followers_count", 0),
                abs(
                    datetime.strptime(
                        tweet["user"].get("created_at", curr_time.strftime(dt_format)),
                        dt_format,
                    )
                    - curr_time
                ).days,
                [
                    tweet["user"].get("default_profile"),
                    tweet["user"].get("default_profile_image"),
                ],
            )
            if "user" in tweet
            else (None, None, None, None, None, None)
        )

        text = self.cleanList(
            tweet["extended_tweet"].get("full_text", tweet.get("text", ""))
            if tweet.get("truncated")
            else (
                (
                    tweet["retweeted_status"].get(
                        "full_text", tweet["retweeted_status"].get("text", "")
                    )
                )
                if retweeted
                else (
                    tweet["quoted_status"].get(
                        "full_text", tweet["quoted_status"].get("text", "")
                    )
                    if quoted
                    else tweet.get("text", "")
                )
            )
        )

        quote_count = tweet.get("quote_count")
        reply_count = tweet.get("reply_count")
        retweet_count = tweet.get("retweet_count")
        favorite_count = tweet.get("favorite_count")

        entities = (
            tweet.get("entities")
            if not tweet.get("truncated")
            else tweet["extended_tweet"].get("entities")
        )
        mList = (
            [x["screen_name"] for x in entities.get("user_mentions", [])]
            if entities
            else []
        )
        hList = [x["text"] for x in entities.get("hashtags", [])] if entities else []
        mediaList = (
            [
                {"type": x.get("type"), "link": x.get("media_url")}
                for x in entities.get("media", [])
            ]
            if entities
            else []
        )
        source = tweet.get("source")

        exactcoord = tweet.get("coordinates")
        coordinates = exactcoord.get("coordinates") if exactcoord else None
        geoenabled = (
            tweet["user"].get("geo_enabled", False) if "user" in tweet else False
        )
        location = tweet["user"].get("location") if "user" in tweet else None

        place_name, place_country, place_countrycode, place_coordinates = (
            (
                tweet["place"].get("full_name"),
                tweet["place"].get("country"),
                tweet["place"].get("country_code"),
                tweet["place"].get("bounding_box", {"coordinates": []})["coordinates"],
            )
            if geoenabled and not text.startswith("RT") and tweet.get("place")
            else (None, None, None, None)
        )

        return {
            "_id": tweet_id,
            "date": created,
            "username": username,
            "description": description,
            "verified": verified,
            "followers": followers,
            "account_age": account_age,
            "defaults": defaults,
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
            "is_retweeted": retweeted,
            "is_quoted": quoted,
        }

    def on_data(self, data):

        super().on_data(data)
        self.total_tweets_count += 1

        t = json.loads(data)
        tweet = self.processTweets(t)

        if (tweet["country_code"] == "GB" or tweet["place_country"] == "United Kingdom"):
            self.collected_tweets_count += 1
            for media in tweet["media"]:
                self.media_count[media["type"]] = self.media_count.get(media["type"], 0) + 1
            self.collector.add(tweet)

        if self.collected_tweets_count >= 180:
            self.analyser.analyse()