import re
import json
import emoji
from tweepy import StreamListener
from datetime import datetime

from . import db, collection
from .dataAnalyser import dataAnalyser


class StreamListener(StreamListener):
    """
    A class provided by tweepy to access the Twitter Streaming API.
    """

    def __init__(self, **kwargs):
        self.total_tweets_count = 0
        self.collected_tweets = []
        self.analyser = dataAnalyser()
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
            tweet["extended_tweet"]["full_text"]
            if tweet.get("truncated")
            else (
                (
                    tweet["retweeted_status"]["extended_tweet"]["full_text"]
                    if tweet["retweeted_status"].get("truncated")
                    else tweet["retweeted_status"].get(
                        "full_text", tweet["retweeted_status"]["text"]
                    )
                )
                if tweet.get("text", "").startswith("RT")
                and "retweeted_status" in tweet
                else tweet.get("text", "")
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
        }

    def on_data(self, data):

        super().on_data(data)
        self.total_tweets_count += 1

        t = json.loads(data)
        tweet = self.processTweets(t)
        #print(tweet["text"])
        #print(self.analyser.tokenize(tweet["text"]))

        if (tweet["country_code"] == "GB" or tweet["place_country"] == "United Kingdom") and self.analyser.get_weight("user", **tweet) > 0.8:
            self.collected_tweets.append(tweet["text"])
            collection.insert_one(tweet)

        if len(self.collected_tweets) > 100:
            self.analyser.analyse(self.collected_tweets)