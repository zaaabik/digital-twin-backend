"""Root file of service running REST api."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException

from database.Interface import DataBase
from database.mongo import MongoDataBase
from language_model.DialogLLM import DialogLLM
from language_model.model import LanguageModel
from utils.logger import get_pylogger

log = get_pylogger(__name__)
logging.basicConfig(level=logging.INFO)

mongo_user_name = os.environ["MONGO_USER_NAME"]
mongo_user_password = os.environ["MONGO_USER_PASSWORD"]
HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_NAME = os.environ["MODEL_NAME"]
CONTEXT_SIZE = 8

connection_string = (
    f"mongodb+srv://{mongo_user_name}:{mongo_user_password}"
    "@cluster0.3xrjcun.mongodb.net/?retryWrites=true&w=majority"
)
TABLE_NAME = "users"
DATABASE_NAME = "chat"

log.info("Open database connection")
database: DataBase = MongoDataBase(
    connection_string=connection_string, database_name=DATABASE_NAME, table_name=TABLE_NAME
)

log.info("Building LM model")
lm: LanguageModel = DialogLLM(hf_token=HF_TOKEN, model_name=MODEL_NAME)

app = FastAPI()

USER_STRING = "@@ВТОРОЙ@@"
BOT_STRING = "@@ПЕРВЫЙ@@"


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

    full_context = user.context
    context = full_context[-(CONTEXT_SIZE - 1) :]
    user_text_with_prefix = f"{USER_STRING} {text}"

    context += (user_text_with_prefix,)
    str_context = " ".join(context)
    context_for_generation = f"{str_context} {BOT_STRING}"
    log.info("Context for model generation %s", context_for_generation)

    model_response = lm.generate(context_for_generation)
    # find start of user tokens and return all before them
    pure_response: str = model_response[: model_response.find(USER_STRING)]
    pure_response = pure_response.rstrip(" ")

    model_text_with_prefix = f"{BOT_STRING} {pure_response}"
    database.update_user_text(
        object_id=object_id, texts=(user_text_with_prefix, model_text_with_prefix)
    )
    log.info("update_user_text model answer")

    return {"bot_answer": pure_response}
