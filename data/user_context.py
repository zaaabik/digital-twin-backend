from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserContext:
    r"""Class hold whole user information."""

    telegram_user_id: str
    username: str | None
    context: list[UserMessage]


@dataclass
class UserMessage:
    r"""Class hold user messages."""
    role: str
    context: str
