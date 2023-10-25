from abc import ABC, abstractmethod

from transformers import PreTrainedTokenizer


class LanguageModel(ABC):
    tokenizer: PreTrainedTokenizer = None

    @abstractmethod
    def generate(self, context) -> str:
        pass
