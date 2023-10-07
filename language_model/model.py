from abc import abstractmethod, ABC


class LanguageModel(ABC):
    @abstractmethod
    def generate(self, context) -> str:
        pass
