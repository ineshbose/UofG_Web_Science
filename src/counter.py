class Counter:
    total_tweets_count = 0
    collected_tweets_count = 0
    media_count = {}
    retweets = 0
    quotes = 0

    @staticmethod
    def count_collected(tweet):
        Counter.collected_tweets_count += 1
        for media in tweet["media"]:
            Counter.media_count[media["type"]] = (
                Counter.media_count.get(media["type"], 0) + 1
            )
        if tweet.get("is_retweeted"):
            Counter.retweets += 1
        if tweet.get("is_quoted"):
            Counter.quotes += 1

    @staticmethod
    def display():
        print(chr(27) + "[2J")
        print(
            "=====================================",
            f"Total Tweets: {Counter.total_tweets_count}",
            f"Collected Tweets: {Counter.collected_tweets_count}",
            f"Retweets: {Counter.retweets}",
            f"Quotes: {Counter.quotes}",
            f"Media: {Counter.media_count}",
            "=====================================",
            sep="\n"
        )
