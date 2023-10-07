from abc import ABC, abstractmethod

from data.user_context import UserContext


class DataBase(ABC):
    @abstractmethod
    def __init__(self, connection_string: str, database_name: str, table_name: str):
        super().__init__()

    @abstractmethod
    def create_user_if_not_exists(self, telegram_user_id: str, username: str):
        pass

    @abstractmethod
    def update_user_text(self,
                         telegram_user_id: str,
                         text: str):
        pass

    @abstractmethod
    def remove_user(self, telegram_user_id: str):
        pass

    @abstractmethod
    def get_user(self, telegram_user_id: str) -> UserContext:
        pass


