from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from data.user_context import BaseMessage, User


class DataBase(ABC):
    @abstractmethod
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        super().__init__()

    @abstractmethod
    def get_all_users(self) -> Any:
        r"""Return all users."""

    @abstractmethod
    def update_model_answer(self, user_id: str, message_id: str, content: str) -> Any:
        r"""
        Update model answer
        Args:
            user_id:
            message_id:
            content:
        """

    @abstractmethod
    def create_user(self, user_id: str, username: str | None, chat_id: str):
        r"""
        Create new user
        Args:
            user_id:
            chat_id:
            username:
        """

    @abstractmethod
    def get_object_id_by_user_id(self, user_id: str) -> Any:
        r"""
        Return Mongo database ID by user id
        Args:
            user_id: unique user id
        """

    # @abstractmethod
    # def find_or_create_user_if_not_exists(self, user_id: str, username: str | None):
    #     r"""
    #     Create new user or return if it exists
    #     Args:
    #         user_id: unique user id
    #         username: user short name
    #     """

    @abstractmethod
    def update_user_text(self, user_id: str, texts: list[BaseMessage]) -> None:
        r"""
        Add conversation to exists user
        Args:
            user_id: unique user id
            texts: Tuple of conversation parts
        """

    @abstractmethod
    def remove_user(self, user_id: str) -> None:
        r"""
        Remove user by user id or doing nothing if it not exists
        Args:
            user_id: unique user id
        """

    @abstractmethod
    def get_user(self, user_id: str) -> User | None:
        r"""
        Get user object by object id
        Args:
            user_id: unique user id
        """

    @abstractmethod
    def get_context(self, user_id: str, limit: int) -> tuple[BaseMessage, list[BaseMessage]]:
        r"""Get user object by object id.

        Args:
            user_id: unique user id
            limit: max number of messages
        """

    @abstractmethod
    def clear_history(self, user_id: str) -> None:
        r"""
        Remove messages of user
        Args:
            user_id: User id passed to store in database
        """

    @abstractmethod
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

    @abstractmethod
    def update_user_choice(self, user_id: str, answer_id: str, user_choice_idx: str) -> str:
        r"""
        Update ids in message
        Args:
            user_id: User id passed to store in database
            user_choice_idx: id of message user chosen
            answer_id: answer id storing in DB
        """

    @abstractmethod
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
