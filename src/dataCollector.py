from . import client


class DataCollector:

    def __init__(self):
        self.client = client
        self.default_db = "Twitter"
        self.default_collection = "Data"
        self.duplicate_count = 0

    def clear(self, db=None, collection=None):
        self.client[db if db else self.default_db][
            collection if collection else self.default_collection
        ].drop()

    def check_duplicate(self, data, db=None, collection=None):
        ids = [d["_id"] for d in self.get_all(db, collection)]
        dup_count = [
            d["_id"]
            for d in ([data] if not isinstance(data, list) else data)
            if d["_id"] in ids
        ]
        self.duplicate_count += len(dup_count)
        return dup_count

    def add(self, data, db=None, collection=None):
        return (
            (
                self.client[db if db else self.default_db][
                    collection if collection else self.default_collection
                ].insert_one(data)
                if not isinstance(data, list)
                else self.client[db if db else self.default_db][
                    collection if collection else self.default_collection
                ].insert_many(data)
            )
            if not self.check_duplicate(data, db, collection)
            else None
        )

    def get_all(self, db=None, collection=None):
        return list(
            self.client[db if db else self.default_db][
                collection if collection else self.default_collection
            ].find({})
        )
