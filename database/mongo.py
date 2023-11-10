from __future__ import annotations

from dataclasses import asdict
from typing import Any

from pymongo import MongoClient

from data.user_context import BaseMessage, ModelAnswer, RoleEnum, User
from database.Interface import DataBase

BASE_PROMPT = "Ты цифровой двойник Артема Заболотного, ты должен поддерживать беседу с друзями и быть веселым."
CUSTOM_USER_CHOICE = "CUSTOM"


class MongoDataBase(DataBase):
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        client: MongoClient = MongoClient(connection_string)
        db = client.get_database(database_name)
        self.collection = db.get_collection(table_name)

    def create_user(self, user_id: str, username: str | None, chat_id: str):
        r"""
        Create new user
        Args:
            user_id:
            username:
            chat_id:
        """

        doc = self.collection.find_one({"user_id": user_id})
        if doc:
            raise ValueError(f"User with user_id:{user_id} already exists")

        system_prompt = BaseMessage(RoleEnum.system, RoleEnum.system, BASE_PROMPT)

        bson = asdict(
            User(
                user_id=user_id,
                username=username,
                chat_id=chat_id,
                system_prompt=system_prompt,
                context=[],
                current_context_start_idx=0,
            )
        )
        self.collection.insert_one(bson)

    def update_model_answer(self, user_id: str, message_id: str, content: str) -> Any:
        r"""
        Update model answer
        Args:
            user_id:
            message_id:
            content:
        """

    def get_all_users(self) -> Any:
        cursor = self.collection.find({})
        users = []
        for document in cursor:
            users.append(User.from_bson(document))
        return users

    def update_user_text(self, user_id: str, texts: list[BaseMessage]) -> None:
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
            [{"$set": {"current_context_start_idx": {"$size": "$context"}}}],
        )

    def get_user(self, user_id: str) -> User | None:
        r"""
        Get user object by user id
        Args:
            user_id: unique user id
        """
        user_bson = self.collection.find_one({"user_id": user_id})
        if not user_bson:
            return None

        return User.from_bson(user_bson)

    def get_context(self, user_id: str, limit: int) -> tuple[BaseMessage, list[BaseMessage]]:
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
                            "$slice": ["$context", "$current_context_start_idx", 100_000]
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
        system_prompt_bson = self.collection.find_one({"user_id": user_id})
        if not system_prompt_bson:
            raise ValueError("Cannot find user!")
        system_prompt = BaseMessage(**system_prompt_bson["system_prompt"])
        if not element:
            return system_prompt, []

        responses = []
        for elem in element["filtered_messages"]:
            if elem["role"] == RoleEnum.user:
                parsed_object = BaseMessage(**elem)
            else:
                parsed_object = ModelAnswer(**elem)

            responses.append(parsed_object)

        return system_prompt, responses

    def set_message_possible_context_ids(
        self, user_id: str, answer_id: str, possible_contexts_ids: list[str]
    ) -> None:
        r"""
        Update ids in message
        Args:
            user_id: User id passed to store in database
            possible_contexts_ids: ids of model answer messages
            answer_id: id of answer storing in database
        """
        self.collection.update_one(
            {
                "user_id": user_id,
                "context.id": answer_id,
            },
            {"$set": {"context.$.possible_contexts_ids": possible_contexts_ids}},
        )

    def update_user_choice(self, user_id: str, answer_id: str, user_choice_idx: str) -> str:
        r"""
        Update ids in message
        Args:
            user_id: User id passed to store in database
            user_choice_idx: id of message user chosen
            answer_id: answer id storing in DB
        """

        self.collection.update_one(
            {
                "user_id": user_id,
                "context.id": answer_id,
            },
            {"$set": {"context.$.user_choice": user_choice_idx}},
        )

        user_message = self.collection.find_one(
            {
                "user_id": user_id,
                "context.id": answer_id,
            },
            {"context.$": 1},
        )
        if not user_message:
            raise ValueError(
                f"Can not find user message. user_id: {user_id} answer_id: {answer_id}"
            )

        message = user_message["context"][0]

        possible_contexts = message["possible_contexts"]
        user_choice = message["user_choice"]
        possible_contexts_ids: list = message["possible_contexts_ids"]
        index_of_user_choice = possible_contexts_ids.index(user_choice)
        user_choice_text = possible_contexts[index_of_user_choice]

        self.collection.update_one(
            {
                "user_id": user_id,
                "context.id": answer_id,
            },
            {"$set": {"context.$.context": user_choice_text}},
        )

        return user_choice_text

    def update_user_custom_choice(
        self, user_id: str, message_choice_id: str, custom_text: str
    ) -> None:
        r"""
        Update ids in message
        Args:
            user_id: User id passed to store in database
            custom_text: text of user variant of answer
            message_choice_id: id of message that was variant of model output
        """
        print(user_id, message_choice_id)
        print(
            self.collection.find_one(
                {
                    "user_id": user_id,
                    "context.possible_contexts_ids": message_choice_id,
                }
            )
        )
        self.collection.update_one(
            {
                "user_id": user_id,
                "context.possible_contexts_ids": message_choice_id,
            },
            {"$set": {"context.$.user_choice": "custom", "context.$.context": custom_text}},
        )
