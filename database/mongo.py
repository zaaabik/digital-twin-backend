from dataclasses import asdict

from pymongo import MongoClient

from data.user_context import UserContext
from database.Interface import DataBase


class MongoDataBase(DataBase):
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        client = MongoClient(connection_string)
        db = client.get_database(database_name)
        self.collection = db.get_collection(table_name)

    def create_user(self, telegram_user_id: str, username: str):
        r"""
        Create new user
        Args:
            telegram_user_id: telegram id
            username:
        """
        bson = asdict(
            UserContext(telegram_user_id=telegram_user_id, username=username, context=())
        )
        insert_result = self.collection.insert_one(bson)
        return insert_result.inserted_id

    def find_or_create_user_if_not_exists(self, telegram_user_id: str, username: str):
        r"""
        Create new user or return if it exists
        Args:
            telegram_user_id: telegram id
            username:
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if doc:
            return doc["_id"]
        else:
            return self.create_user(telegram_user_id, username)

    def update_user_text(self, object_id: str, texts: tuple):
        r"""
        Add conversation to exists user
        Args:
            object_id: Mongo database ID
            texts: Tuple of conversation parts
        """
        return self.collection.update_one(
            {"_id": object_id}, {"$push": {"context": {"$each": texts}}}
        )

    def get_object_id_by_telegram_id(self, telegram_user_id: str):
        r"""
        Return Mongo database ID by telegram id
        Args:
            telegram_user_id:
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if doc:
            return doc["_id"]
        return

    def remove_user(self, telegram_user_id: str):
        r"""
        Remove user by telegram user id or doing nothing if it not exists
        Args:
            telegram_user_id: User id passed to store in database
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if not doc:
            return
        return self.collection.delete_one({"_id": doc["_id"]})

    def get_user(self, object_id: str) -> UserContext:
        r"""
        Get user object by object id
        Args:
            object_id: Mongo database ID
        """
        user_bson = self.collection.find_one({"_id": object_id})
        user_bson.pop("_id")
        return UserContext(**user_bson)
