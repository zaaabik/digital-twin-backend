"""Root file of service running REST api."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException

from data.user_context import UserMessage
from database.Interface import DataBase
from database.mongo import MongoDataBase
from language_model.LLama import LLama
from language_model.model import LanguageModel
from utils.logger import get_pylogger

log = get_pylogger(__name__)
logging.basicConfig(level=logging.INFO)

connection_string = os.environ["DATABASE_CONNECTION_STRING"]
HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_NAME = os.environ["MODEL_NAME"]
CONTEXT_SIZE = int(os.environ["CONTEXT_SIZE"])

TABLE_NAME = "users"
DATABASE_NAME = "chat"

log.info("Open database connection")
database: DataBase = MongoDataBase(
    connection_string=connection_string, database_name=DATABASE_NAME, table_name=TABLE_NAME
)

log.info("Building LM model")
lm: LanguageModel = LLama(hf_token=HF_TOKEN, model_name=MODEL_NAME)

app = FastAPI()


@app.get("/ping")
def ping():
    r"""Health check route."""
    return {"ping": "pong"}


@app.delete("/dialog/{user_id}")
def delete_user(user_id: str):
    r"""
    Remove all information about user from database
    Args:
        user_id: User id passed to store in database
    """
    telegram_user_id: str = user_id
    database.remove_user(telegram_user_id=telegram_user_id)
    log.info("Remove user %s", telegram_user_id)
    return {}


@app.get("/dialog/{user_id}")
def get_user(user_id: str):
    r"""
    Get all user property by user id
    Args:
        user_id: User id passed to store in database
    """
    telegram_user_id: str = user_id

    object_id = database.get_object_id_by_telegram_id(telegram_user_id=telegram_user_id)
    if not object_id:
        raise HTTPException(status_code=404, detail="Item not found")

    user = database.get_user(object_id=object_id)
    return user


def generate_dialog(messages: list[UserMessage]):
    template = "<s> {role}: {content}\n</s>"
    text = ""
    for message in messages:
        text += template.format(role=message.role, content=message.context)
    text += "<s> bot: "
    return text


@app.patch("/dialog/{user_id}")
def update_user_messages(user_id: str, text: str, username: str = ""):
    r"""
    Update state of user, run language model and return response
    Args:
        user_id: User id passed to store in database
        text: User message
        username: Additional information about user
            Default: ``None``
    """
    telegram_user_id: str = user_id

    object_id = database.find_or_create_user_if_not_exists(
        telegram_user_id=telegram_user_id, username=username
    )
    log.info("create_user_if_not_exists")

    user = database.get_user(object_id=object_id)
    if not user:
        log.error("Error while getting user telegram_user_id=%s", telegram_user_id)
        raise OSError("Error while getting user telegram_user_id")
    user_question = UserMessage(role="user", context=text)
    context_for_generation = [user.system_prompt] + user.context[-CONTEXT_SIZE:] + [user_question]

    full_context = generate_dialog(context_for_generation)

    log.info("Context for model generation %s", full_context)

    model_response = lm.generate(full_context)
    # find start of user tokens and return all before them
    pure_response: str = model_response

    model_answer = UserMessage(role="bot", context=pure_response)
    database.update_user_text(object_id=object_id, texts=[user_question, model_answer])
    log.info("update_user_text model answer")

    return {"bot_answer": model_answer}
