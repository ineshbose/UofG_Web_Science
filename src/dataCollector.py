from . import client


class DataCollector:
    def __init__(self):
        self.client = client
        self.default_db = "Twitter"
        self.default_collection = "Data"

    def clear(self, db=None, collection=None):
        self.client[db if db else self.default_db][
            collection if collection else self.default_collection
        ].drop()

    def add(self, data, db=None, collection=None):
        return (
            self.client[db if db else self.default_db][
                collection if collection else self.default_collection
            ].insert_one(data)
            if not isinstance(data, list)
            else self.client[db if db else self.default_db][
                collection if collection else self.default_collection
            ].insert_many(data)
        )

    def get_all(self, db=None, collection=None):
        return self.client[db if db else self.default_db][
            collection if collection else self.default_collection
        ].find({})
