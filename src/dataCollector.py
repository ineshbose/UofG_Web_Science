from . import client

class DataCollector:

    def __init__(self):
        self.client = client
        self.default_db = "Twitter"
        self.default_collection = "Data"

    def clear(self, db=self.default_db, collection=self.default_collection):
        self.client[db][collection].drop()

    def add(self, data, db=self.default_db, collection=self.default_collection):
        return (
            self.client[db][collection].insert_one(data)
            if type(data) != type(list) else
            self.client[db][collection].insert_many(data)
        )

    def get_all(self, db=self.default_db, collection=self.default_collection):
        return self.client[db][collection].find({})