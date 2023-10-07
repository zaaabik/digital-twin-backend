from pymongo import MongoClient

from data.user_context import UserContext
from dataclasses import asdict

from database.Interface import DataBase


class MongoDataBase(DataBase):
    def __init__(self,
                 connection_string: str,
                 database_name: str,
                 table_name: str):
        client = MongoClient(connection_string)
        db = client.get_database(database_name)
        self.collection = db.get_collection(table_name)

    def create_user_if_not_exists(self, telegram_user_id: str, username: str):
        doc = self.collection.find_one({'telegram_user_id': telegram_user_id})
        if not doc:
            bson = asdict(
                UserContext(telegram_user_id=telegram_user_id, username=username, context=())
            )
            self.collection.insert_one(bson)

    def update_user_text(self, telegram_user_id: str, text: str):
        doc = self.collection.find_one({'telegram_user_id': telegram_user_id})
        return self.collection.update_one(
            {'_id': doc['_id']},
            {'$push': {'context': text}}
        )

    def remove_user(self, telegram_user_id: str):
        doc = self.collection.find_one({'telegram_user_id': telegram_user_id})
        return self.collection.delete_one(
            {'_id': doc['_id']}
        )

    def get_user(self, telegram_user_id: str) -> UserContext:
        user_bson = self.collection.find_one({'telegram_user_id': telegram_user_id})
        user_bson.pop('_id')
        return UserContext(**user_bson)
