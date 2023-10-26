"""Root file of service running REST api."""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from transformers import AutoTokenizer

from api.language_model import LanguageModelAPI
from data.user_context import UserMessage
from database.Interface import DataBase
from database.mongo import MongoDataBase
from language_model.Chat import Conversation
from utils.logger import get_pylogger

log = get_pylogger(__name__)
logging.basicConfig(level=logging.INFO)

connection_string = os.environ["DATABASE_CONNECTION_STRING"]
TEMPLATE_PATH = os.environ["TEMPLATE_PATH"]
HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_NAME = os.environ["MODEL_NAME"]
LM_API_ADDRESS = os.environ["LM_API_ADDRESS"]
CONTEXT_SIZE = int(os.environ["CONTEXT_SIZE"])
TABLE_NAME = "users"
DATABASE_NAME = "chat"

log.info("Open database connection")
database: DataBase = MongoDataBase(
    connection_string=connection_string, database_name=DATABASE_NAME, table_name=TABLE_NAME
)

log.info("Building tokenizer model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

lm_api = LanguageModelAPI(LM_API_ADDRESS)

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


@app.get("/dialog")
def get_users():
    r"""Get all user."""
    all_users = database.get_all_users()
    return all_users


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
    context_for_generation: list[UserMessage] = user.context[-CONTEXT_SIZE:] + [user_question]

    conversation = Conversation.from_template(TEMPLATE_PATH)
    conversation.expand(context_for_generation)
    text_for_generation = conversation.get_prompt_for_generate(tokenizer)
    log.info("Context for model generation %s", text_for_generation)

    model_response = lm_api.generate(text_for_generation)
    # find start of user tokens and return all before them
    pure_response: str = model_response

    model_answer = UserMessage(role="bot", context=pure_response)
    database.update_user_text(object_id=object_id, texts=[user_question, model_answer])
    log.info("update_user_text model answer")

    return {"bot_answer": model_answer}
