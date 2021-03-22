from src.dataCollector import DataCollector

collector = DataCollector()

if __name__ == "__main__":
    data = collector.get_all()
    print(
        f"Total Collected Tweets: {len(data)}",
        f'Quotes: {sum(1 for d in data if d.get("is_quoted"))}',
        f'Retweets : {sum(1 for d in data if d.get("is_retweeted"))}',
        f'Media : {sum(1 for d in data if d.get("media"))}',
        f'Images : {sum(1 for d in data for m in d["media"] if m.get("type") == "photo")}',
        f'Verified : {sum(1 for d in data if d.get("verified"))}',
        f'Geotagged : {sum(1 for d in data if d.get("geoenabled"))}',
        f'Location : {sum(1 for d in data if d.get("location"))}',
        sep="\n",
    )