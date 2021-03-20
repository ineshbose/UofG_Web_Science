import time

from src import api, filters, streamer

streamer.filter(
    locations=filters.locations, track=filters.words, languages=["en"], is_async=False
)
'''
last_id = None
counter = 0
sinceID = None

results = False

while counter < 1:
    if counter < 1:
        results = api.search(
            geocode=filters.geocode,
            count=1,
            lang="en",
            tweet_mode="extended",
            max_id=last_id,
        )  # , since_id = sinceID)
        for r in results:
            print(r)
        counter += 1
    """
    else:
        time.sleep(15 * 60)
    """
'''
