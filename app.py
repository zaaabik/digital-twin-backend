"""Root file of service running REST api."""
from __future__ import annotations

import logging
import os

from bson.objectid import ObjectId
from fastapi import FastAPI, status
from huggingface_hub import login as hf_login
from transformers import AutoTokenizer

from api.language_model import LanguageModelAPI
from data.base_classes import (
    GenerateRequest,
    GenerationChoiceResponse,
    SetMessagePossibleContextIds,
    SetUserChoice,
    SetUserCustomAnswer,
    UserCreateRequest,
)
from data.user_context import BaseMessage, ModelAnswer, RoleEnum
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
TABLE_NAME = os.environ["TABLE_NAME"]
DATABASE_NAME = "chat"

log.info("Open database connection")
database: DataBase = MongoDataBase(
    connection_string=connection_string, database_name=DATABASE_NAME, table_name=TABLE_NAME
)

log.info("Logging into HF")
hf_login(HF_TOKEN)

log.info("Building tokenizer model")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

lm_api = LanguageModelAPI(LM_API_ADDRESS)

app = FastAPI()


@app.get("/ping")
def ping():
    r"""Health check route."""
    return {"ping": "pong"}


@app.post("/users", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreateRequest):
    r"""Create new user."""
    try:
        database.create_user(user_id=user.user_id, username=user.username, chat_id=user.chat_id)
    except ValueError:
        pass

    return {"user_id": user.user_id}


@app.delete("/users/{user_id}/context")
def clear_history(user_id: str):
    r"""
    Remove all user messages
    Args:
        user_id: User id passed to store in database
    """
    database.clear_history(user_id=user_id)
    log.info("Clear history user %s", user_id)
    return {"status": "history_cleared"}


@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: str):
    r"""
    Remove all information about user from database
    Args:
        user_id: User id passed to store in database
    """
    database.remove_user(user_id=user_id)
    log.info("Remove user %s", user_id)
    return {"user_id": user_id}


@app.get("/users/{user_id}")
def get_user(user_id: str):
    r"""
    Get all user property by user id
    Args:
        user_id: User id passed to store in database
    """
    user = database.get_user(user_id=user_id)
    return user


@app.get("/users")
def get_users():
    r"""Get all user."""
    all_users = database.get_all_users()
    return all_users


@app.get("/users/{user_id}/context")
def get_users_not_deleted_messages(user_id: str, limit: int):
    r"""Get all user."""
    messages = database.get_context(user_id, limit)
    return messages


@app.patch("/users/{user_id}/context/generate")
def generate(user_id: str, generate_request: GenerateRequest):
    r"""
    Update state of user, run language model and return response
    Args:
        user_id: id of user, must be unique
        generate_request: user question
    """

    system_prompt, user_messages = database.get_context(user_id, CONTEXT_SIZE)
    user_question = BaseMessage(
        id=str(ObjectId()), role=RoleEnum.user, context=generate_request.text
    )

    context_for_generation: list[BaseMessage] = user_messages + [user_question]

    conversation = Conversation.from_template(TEMPLATE_PATH, system_prompt=system_prompt.context)
    conversation.expand(context_for_generation)
    text_for_generation = conversation.get_prompt_for_generate(tokenizer)
    log.info("Context for model generation %s", text_for_generation)

    model_response = lm_api.generate(text_for_generation)
    model_answer_id = str(ObjectId())
    model_answer = ModelAnswer(
        id=model_answer_id,
        role=RoleEnum.bot,
        context=model_response.texts[0],
        possible_contexts=model_response.texts,
        user_choice=False,
        possible_contexts_ids=[],
    )
    database.update_user_text(user_id=user_id, texts=[user_question, model_answer])
    log.info("update_user_text model answer")
    print(model_response.texts)
    return GenerationChoiceResponse(messages=model_response.texts, answer_id=model_answer_id)


@app.post("/users/{user_id}/context/{answer_id}/possible_contexts_ids")
def set_message_possible_context_ids(
    user_id: str, answer_id: str, set_message_possible_ids: SetMessagePossibleContextIds
):
    r"""
    Update state of message
    Args:
        user_id: id of user, must be unique
        answer_id: DB id of model answer
        set_message_possible_ids: id of messages proposed by model
    """
    database.set_message_possible_context_ids(
        user_id, answer_id, set_message_possible_ids.possible_contexts_ids
    )
    return {"ids": set_message_possible_ids.possible_contexts_ids}


@app.post("/users/{user_id}/context/messages/custom_answer")
def set_user_choice_custom_answer(user_id: str, user_custom_answer: SetUserCustomAnswer):
    r"""
    Update state of message
    Args:
        user_id: id of user, must be unique
        user_custom_answer: text of user proposed answer
    """
    database.update_user_custom_choice(
        user_id, user_custom_answer.message_id, user_custom_answer.custom_text
    )
    return {"text": user_custom_answer.custom_text}


@app.post("/users/{user_id}/context/{answer_id}/user_choice")
def set_user_choice_answer(user_id: str, answer_id: str, user_choice: SetUserChoice):
    r"""
    Update state of message
    Args:
        user_id: id of user, must be unique
        answer_id: DB id of model answer
        user_choice: id of message chosen by the user
    """
    choice_text = database.update_user_choice(user_id, answer_id, user_choice.message_id)
    return {"text": choice_text}
