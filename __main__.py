from src import cursor, filters, streamer, analyser


streamer.filter(locations=filters.locations, track=filters.words, languages=["en"], is_async=True)
cursor.search(geocode=filters.geocode, count=100, lang="en", tweet_mode="extended", is_async=True)
analyser.analyse()