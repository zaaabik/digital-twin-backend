# pylint: disable=no-name-in-module

from pydantic import BaseModel


class GenerateRequest(BaseModel):
    text: str
    username: str
