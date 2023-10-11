from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserContext:
    telegram_user_id: str
    username: str | None
    context: tuple[()] | tuple[str]
