import logging
import os

from database.Interface import DataBase
from database.mongo import MongoDataBase
from language_model.DialogLLM import DialogLLM
from language_model.model import LanguageModel
from utils.logger import get_pylogger

log = get_pylogger(__name__)
logging.basicConfig(level=logging.INFO)

from typing import Union

from fastapi import FastAPI

mongo_user_name = os.getenv("MONGO_USER_NAME")
mongo_user_password = os.getenv("MONGO_USER_PASSWORD")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = os.getenv("MODEL_NAME")
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
    log.info(f"Remove user {telegram_user_id}")
    return {}


@app.patch("/dialog/{user_id}")
def update_user_messages(user_id: str, text: str, username: Union[str, None] = None):
    r"""
    Update state of user, run language model and return response
    Args:
        user_id: User id passed to store in database
        text: User message
        username: Additional information about user
            Default: ``None``
    """
    telegram_user_id: str = user_id
    text_with_prefix = f"@@ВТОРОЙ@@ {text}"

    database.create_user_if_not_exists(telegram_user_id=telegram_user_id, username=username)
    log.info("create_user_if_not_exists")

    database.update_user_text(telegram_user_id=telegram_user_id, text=text_with_prefix)
    log.info("update_user_text")

    user = database.get_user(telegram_user_id=telegram_user_id)
    full_context = user.context
    context = full_context[-CONTEXT_SIZE:]
    str_context = " ".join(context)
    context_for_generation = f"{str_context} @@ПЕРВЫЙ@@"
    log.info(f"Context for model generation: {context_for_generation}")

    model_response = lm.generate(context_for_generation)
    pure_response: str = model_response[: model_response.find("@@ВТОРОЙ@@")]
    pure_response = pure_response.rstrip(" ")

    model_response_to_db = f"@@ПЕРВЫЙ@@ {pure_response}"
    database.update_user_text(telegram_user_id=telegram_user_id, text=model_response_to_db)
    log.info("update_user_text model answer")

    return {"response": pure_response, "full_text": model_response}
