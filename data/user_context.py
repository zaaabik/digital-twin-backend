from __future__ import annotations

from dataclasses import dataclass


@dataclass
class User:
    r"""Class hold whole user information."""

    user_id: str
    username: str | None
    chat_id: str
    current_context_start_idx: int
    system_prompt: BaseMessage
    context: list[BaseMessage]

    @classmethod
    def from_bson(cls, user_bson):
        user_bson = user_bson.copy()
        user_bson.pop("_id")
        context = []
        for o in user_bson["context"]:
            context.append(BaseMessage(role=o["role"], context=o["context"], id=o["id"]))
        if "system_prompt" in user_bson:
            system_prompt_bson = user_bson["system_prompt"]
            system_prompt = BaseMessage(
                role=system_prompt_bson["role"],
                context=system_prompt_bson["context"],
                id=system_prompt_bson["id"],
            )
        else:
            system_prompt = BaseMessage(role="", context="", id="")

        return User(
            user_id=user_bson["user_id"],
            username=user_bson["username"],
            chat_id=user_bson["chat_id"],
            system_prompt=system_prompt,
            context=context,
            current_context_start_idx=user_bson["current_context_start_idx"],
        )


class RoleEnum:
    system = "system"
    bot = "bot"
    user = "user"


@dataclass
class BaseMessage:
    r"""Class hold user messages."""
    id: str
    role: str
    context: str


@dataclass
class ModelAnswer(BaseMessage):
    r"""Class hold model answer with user choice."""
    possible_contexts: list[str]
    user_choice: bool
    possible_contexts_ids: list[str] | None
