from dataclasses import dataclass


@dataclass
class UserContext:
    telegram_user_id: str
    username: str
    context: tuple[str]
