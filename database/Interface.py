from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from data.user_context import UserContext, UserMessage


class DataBase(ABC):
    @abstractmethod
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        super().__init__()

    @abstractmethod
    def get_all_users(self) -> Any:
        r"""Return all users."""

    @abstractmethod
    def get_object_id_by_telegram_id(self, telegram_user_id: str) -> Any:
        r"""
        Return Mongo database ID by telegram id
        Args:
            telegram_user_id:
        """

    @abstractmethod
    def find_or_create_user_if_not_exists(self, telegram_user_id: str, username: str | None):
        r"""
        Create new user or return if it exists
        Args:
            telegram_user_id: telegram id
            username: telegram username
        """

    @abstractmethod
    def update_user_text(self, object_id: str, texts: list[UserMessage]) -> None:
        r"""
        Add conversation to exists user
        Args:
            object_id: Database uniq id
            texts: Tuple of conversation parts
        """

    @abstractmethod
    def remove_user(self, telegram_user_id: str) -> None:
        r"""
        Remove user by telegram user id or doing nothing if it not exists
        Args:
            telegram_user_id: User id passed to store in database
        """

    @abstractmethod
    def get_user(self, object_id: str) -> UserContext | None:
        r"""
        Get user object by object id
        Args:
            object_id: Database uniq id
        """

    @abstractmethod
    def get_user_not_deleted_messages(self, user_id: str, limit: int) -> list[UserMessage] | None:
        r"""
        Get user object by object id
        Args:
            :param user_id: telegram user id
            :param limit: max number of messages
        """

    @abstractmethod
    def clear_history(self, telegram_user_id: str) -> None:
        r"""
        Remove messages of user
        Args:
            telegram_user_id: User id passed to store in database
        """
