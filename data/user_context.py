from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserContext:
    r"""Class hold whole user information."""

    telegram_user_id: str
    username: str | None
    current_message_idx: int
    system_prompt: UserMessage
    context: list[UserMessage]

    @classmethod
    def from_bson(cls, user_bson):
        user_bson = user_bson.copy()
        user_bson.pop("_id")
        context = []
        for o in user_bson["context"]:
            context.append(UserMessage(role=o["role"], context=o["context"]))
        if "system_prompt" in user_bson:
            system_prompt_bson = user_bson["system_prompt"]
            system_prompt = UserMessage(
                role=system_prompt_bson["role"],
                context=system_prompt_bson["context"],
            )
        else:
            system_prompt = UserMessage(role="", context="")

        return UserContext(
            telegram_user_id=user_bson["telegram_user_id"],
            username=user_bson["username"],
            system_prompt=system_prompt,
            context=context,
            current_message_idx=user_bson["current_message_idx"],
        )


@dataclass
class UserMessage:
    r"""Class hold user messages."""
    role: str
    context: str
