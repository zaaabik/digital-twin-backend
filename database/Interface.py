from abc import ABC, abstractmethod

from data.user_context import UserContext


class DataBase(ABC):
    @abstractmethod
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        super().__init__()

    @abstractmethod
    def get_object_id_by_telegram_id(self, telegram_user_id: str):
        r"""
        Return Mongo database ID by telegram id
        Args:
            telegram_user_id:
        """
        pass

    @abstractmethod
    def find_or_create_user_if_not_exists(self, telegram_user_id: str, username: str):
        r"""
        Create new user or return if it exists
        Args:
            telegram_user_id: telegram id
            username:
        """
        pass

    @abstractmethod
    def update_user_text(self, object_id: str, texts: tuple):
        r"""
        Add conversation to exists user
        Args:
            object_id: Database uniq id
            texts: Tuple of conversation parts
        """
        pass

    @abstractmethod
    def remove_user(self, telegram_user_id: str):
        r"""
        Remove user by telegram user id or doing nothing if it not exists
        Args:
            telegram_user_id: User id passed to store in database
        """
        pass

    @abstractmethod
    def get_user(self, object_id: str) -> UserContext:
        r"""
        Get user object by object id
        Args:
            object_id: Database uniq id
        """
        pass
