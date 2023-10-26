import requests

HEADERS = {"Accept": "application/json"}


class LanguageModelAPI:
    def __init__(self, base_api_path):
        self.base_api_path = base_api_path

    def generate(self, text: str):
        path = f"{self.base_api_path}/generate"
        answer = requests.post(url=path, json={"text": text}, timeout=10)
        return answer.json()["generated_text"]
