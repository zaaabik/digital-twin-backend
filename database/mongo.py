from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pymongo import MongoClient

from data.user_context import UserContext, UserMessage
from database.Interface import DataBase


class MongoDataBase(DataBase):
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        client: MongoClient = MongoClient(connection_string)
        db = client.get_database(database_name)
        self.collection = db.get_collection(table_name)

    def create_user(self, user_id: str, username: str | None):
        r"""
        Create new user
        Args:
            user_id:
            username:
        """
        system_prompt = UserMessage("system", "")

        bson = asdict(
            UserContext(
                user_id=user_id,
                username=username,
                system_prompt=system_prompt,
                context=[],
                current_message_idx=0,
            )
        )
        self.collection.insert_one(bson)

    def get_all_users(self) -> Any:
        cursor = self.collection.find({})
        users = []
        for document in cursor:
            users.append(UserContext.from_bson(document))
        return users

    def find_or_create_user_if_not_exists(self, user_id: str, username: str | None):
        r"""
        Create new user or return if it exists
        Args:
            user_id: unique user id
            username: user short name
        """
        doc = self.collection.find_one({"user_id": user_id})
        if doc:
            return
        self.create_user(user_id, username)

    def update_user_text(self, user_id: str, texts: list[UserMessage]) -> None:
        r"""
        Add conversation to exists user
        Args:
            user_id: unique user id
            texts: Tuple of conversation parts
        """
        texts_mapped = [asdict(text) for text in texts]
        self.collection.update_one(
            {"user_id": user_id}, {"$push": {"context": {"$each": texts_mapped}}}
        )

    def get_object_id_by_user_id(self, user_id: str) -> Any:
        r"""
        Return Mongo database ID by user id
        Args:
            user_id: User id passed to store in database
        """
        doc = self.collection.find_one({"user_id": user_id})
        if doc:
            return doc["_id"]
        return None

    def remove_user(self, user_id: str) -> None:
        r"""
        Remove user by user id or doing nothing if it not exists
        Args:
            user_id: User id passed to store in database
        """
        doc = self.collection.find_one({"user_id": user_id})
        if not doc:
            return
        self.collection.delete_one({"_id": doc["_id"]})

    def clear_history(self, user_id: str) -> None:
        r"""
        Remove messages of user
        Args:
            user_id: User id passed to store in database
        """
        self.collection.update_one(
            {"user_id": user_id},
            [{"$set": {"current_message_idx": {"$size": "$context"}}}],
        )

    def get_user(self, user_id: str) -> UserContext | None:
        r"""
        Get user object by user id
        Args:
            user_id: unique user id
        """
        user_bson = self.collection.find_one({"user_id": user_id})
        if not user_bson:
            return None

        return UserContext.from_bson(user_bson)

    def get_user_not_deleted_messages(self, user_id: str, limit: int) -> list[UserMessage] | None:
        r"""
        Get user object by object id
        Args:
            user_id: user id
            limit: max number of messages
        """

        user_messages = self.collection.aggregate(
            [
                {"$match": {"user_id": user_id}},
                {
                    "$project": {
                        "filtered_messages": {
                            "$slice": ["$context", "$current_message_idx", 100_000]
                        }
                    }
                },
                {
                    "$project": {
                        "filtered_messages": {
                            "$lastN": {"input": "$filtered_messages", "n": limit}
                        }
                    }
                },
            ]
        )
        element = user_messages.try_next()
        if not element:
            return None

        return [UserMessage(**i) for i in element["filtered_messages"]]
