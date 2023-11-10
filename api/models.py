# pylint: disable=no-name-in-module
from pydantic import BaseModel


class GenerationResponse(BaseModel):
    r"""
    Request response
    Args:
        texts: multiple variants of answers
    """
    texts: list[str]

    def __init__(self, texts):
        super().__init__()
        self.texts = texts
