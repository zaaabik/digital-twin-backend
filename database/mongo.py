from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pymongo import MongoClient

from data.user_context import UserContext, UserMessage
from database.Interface import DataBase

BASE_SYSTEM_PROMPT = (
    "Меня зовут Артём Заболотный. Тебе 26 лет, ты закончил бакалавриат в университет "
    "аэрокосмического приборостроения, магистратуру в Сколтехе и сейчас учишься в аспирантуре "
    "Сколтеха. Ты работал с 2017 по 2020 в Радарио full-stack разработчиком на C#, GO, VUE, "
    "а сейчас работаешь Senior Data Scientist в RnD отделе сбербанка."
    " Твою девушку зовут Марина и вы с ней живете в Тбилиси, вы с ней знаете друг-друга с 10 класса"
    " но встречаться начали только 11 июня 2023 года."
)


class MongoDataBase(DataBase):
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        client: MongoClient = MongoClient(connection_string)
        db = client.get_database(database_name)
        self.collection = db.get_collection(table_name)

    def create_user(self, telegram_user_id: str, username: str | None):
        r"""
        Create new user
        Args:
            telegram_user_id: telegram id
            username: telegram username
        """
        system_prompt = UserMessage("system", BASE_SYSTEM_PROMPT)

        bson = asdict(
            UserContext(
                telegram_user_id=telegram_user_id,
                username=username,
                system_prompt=system_prompt,
                context=[],
            )
        )
        insert_result = self.collection.insert_one(bson)
        return insert_result.inserted_id

    def get_all_users(self) -> Any:
        cursor = self.collection.find({})
        users = []
        for document in cursor:
            users.append(UserContext.from_bson(document))
        return users

    def find_or_create_user_if_not_exists(self, telegram_user_id: str, username: str | None):
        r"""
        Create new user or return if it exists
        Args:
            telegram_user_id: telegram id
            username: telegram nickname
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if doc:
            return doc["_id"]
        return self.create_user(telegram_user_id, username)

    def update_user_text(self, object_id: str, texts: list[UserMessage]) -> None:
        r"""
        Add conversation to exists user
        Args:
            object_id: Mongo database ID
            texts: Tuple of conversation parts
        """
        texts_mapped = [asdict(text) for text in texts]
        self.collection.update_one(
            {"_id": object_id}, {"$push": {"context": {"$each": texts_mapped}}}
        )

    def get_object_id_by_telegram_id(self, telegram_user_id: str) -> Any:
        r"""
        Return Mongo database ID by telegram id
        Args:
            telegram_user_id:
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if doc:
            return doc["_id"]
        return None

    def remove_user(self, telegram_user_id: str) -> None:
        r"""
        Remove user by telegram user id or doing nothing if it not exists
        Args:
            telegram_user_id: User id passed to store in database
        """
        doc = self.collection.find_one({"telegram_user_id": telegram_user_id})
        if not doc:
            return
        self.collection.delete_one({"_id": doc["_id"]})

    def get_user(self, object_id: str) -> UserContext | None:
        r"""
        Get user object by object id
        Args:
            object_id: Mongo database ID
        """
        user_bson = self.collection.find_one({"_id": object_id})
        if not user_bson:
            return None

        return UserContext.from_bson(user_bson)
