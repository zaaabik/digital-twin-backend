import requests

HEADERS = {"Accept": "application/json"}


class LanguageModelAPI:
    """Class contains methods to work with LLM generation api."""

    def __init__(self, base_api_path):
        self.base_api_path = base_api_path

    def generate(self, text: str):
        """Function will call LLM api and return answer for user :str text: object."""
        path = f"{self.base_api_path}/generate"
        answer = requests.post(url=path, json={"text": text}, timeout=180)
        return answer.json()["generated_text"]
