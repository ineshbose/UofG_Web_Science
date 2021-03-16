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
        self.collected_tweets_count = 0
        self.collected_tweets = []
        self.analyser = dataAnalyser()
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
            f"Total tweets: {self.total_tweets_count}",
            f"Collected tweets: {self.collected_tweets_count}",
            sep="\n"
        )

    def strip_emoji(self, text):
        return re.sub(emoji.get_emoji_regexp(), r"", text)

    def cleanList(self, text):
        text = self.strip_emoji(text)
        text.encode("ascii", errors="ignore").decode()
        return text

    def processTweets(self, tweet):

        curr_time = datetime.now()
        dt_format = "%a %b %d %H:%M:%S +0000 %Y"
        created = datetime.strptime(tweet.get("created_at", curr_time.strftime(dt_format)), dt_format)
        tweet_id = tweet.get("id_str")

        username, description, verified, followers, account_age = (
            tweet["user"].get("screen_name"),
            tweet["user"].get("description"),
            tweet["user"].get("verified"),
            tweet["user"].get("followers_count", 0),
            abs(datetime.strptime(tweet["user"].get("created_at", curr_time.strftime(dt_format)), dt_format) - curr_time).days,
        ) if "user" in tweet else (None, None, None, None, None)

        fw = {range(1): 0, range(1,50): 0.5, range(50,5000): 1.0,range(5000,10000): 1.5,range(10000,100000): 2.0,range(100000,200000): 2.5}
        aw = {range(1): 0, range(1,182): 0.5, range(182, 365): 1.0, range(365, 547): 1.5}
        desc_weight, verified_weight, follow_weight, account_age, profile_weight = (
            (1.0 if description else 0),
            (1.0 if verified else 0),
            ((sum(fw[k] for k in fw if followers in k)/3) if followers in range(200000) else 1.0),
            ((sum(aw[k] for k in aw if account_age in k)/3) if account_age in range(547) else 1.0),
            (0.5 if not tweet["user"].get("default_profile") else 0) + (0.5 if not tweet["user"].get("default_profile_image") else 0),
        )
        quality_score = (profile_weight + verified_weight + follow_weight + account_age + desc_weight)/5

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
            "quality_score": quality_score
        }

    def on_data(self, data):

        super().on_data(data)
        self.total_tweets_count += 1

        t = json.loads(data)
        tweet = self.processTweets(t)

        if tweet["quality_score"] > 0.85 and tweet["place_country"] == "United Kingdom":
            self.collected_tweets_count += 1
            self.collected_tweets.append(tweet["text"])
            collection.insert_one(tweet)

        if self.collected_tweets_count > 100:
            self.analyser.analyse(self.collected_tweets)