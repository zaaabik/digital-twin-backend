import requests

from data.base_classes import GenerationLLMResponse


class LanguageModelAPI:
    """Class contains methods to work with LLM generation api."""

    def __init__(self, base_api_path):
        self.base_api_path = base_api_path

    def generate(self, text: str) -> GenerationLLMResponse:
        """Function will call LLM api and return answer for user text
        Args:
            text: user question with context
        """
        path = f"{self.base_api_path}/generate"
        answer = requests.post(url=path, json={"text": text}, timeout=180).json()
        return GenerationLLMResponse(**answer)
