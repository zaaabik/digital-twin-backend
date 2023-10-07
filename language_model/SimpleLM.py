from language_model.model import LanguageModel


class SimpleLM(LanguageModel):
    def generate(self, context) -> str:
        return 'Привет! @@ВТОРОЙ@@'
