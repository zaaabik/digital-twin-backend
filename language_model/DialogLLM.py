from huggingface_hub import login
from transformers import AutoModelWithLMHead, AutoTokenizer

from language_model.model import LanguageModel


class DialogLLM(LanguageModel):
    r"""Class for generation answers for bot using LLM from huggingface repos."""

    def __init__(self, hf_token: str, model_name: str):
        r"""
        Init class for generation answers for bot
        Args:
            hf_token: hugging face token using for download model
            model_name: LLM model name
        """
        login(hf_token)

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, return_token_type_ids=False, device_map="auto"
        )
        self.model = AutoModelWithLMHead.from_pretrained(model_name)

        self.generation_params = {
            "top_k": 25,
            "top_p": 0.90,
            "num_beams": 2,
            "num_return_sequences": 1,
            "do_sample": True,
            "no_repeat_ngram_size": 2,
            "temperature": 1.2,
            "repetition_penalty": 1.2,
            "length_penalty": -15.0,
            "eos_token_id": 50257,
            "max_new_tokens": 60,
            "sequence_bias": {
                (21,): -10.0,
                self.get_tokens_as_tuple("У тебя как?"): -10.0,
                self.get_tokens_as_tuple("Че делаешь сегодня?"): -10.0,
                self.get_tokens_as_tuple("чувствуешь"): -10.0,
                self.get_tokens_as_tuple("Живой?"): -10.0,
                self.get_tokens_as_tuple("ты как"): -10.0,
                self.get_tokens_as_tuple("Ты как"): -10.0,
                self.get_tokens_as_tuple("Аудиозапись"): -100.0,
                self.get_tokens_as_tuple("А ты?"): -10.0,
                self.get_tokens_as_tuple("как дела"): -10.0,
            },
        }

    def get_tokens_as_tuple(self, word: str):
        r"""
        Return token ids
        Args:
            word: telegram id
        """
        return tuple(self.tokenizer([word], add_special_tokens=False).input_ids[0])

    def generate(self, context: str) -> str:
        r"""
        Return token ids
        Args:
            context: whole dialog using for generation answer
        """
        inputs = self.tokenizer(context, return_tensors="pt")
        generated_token_ids = self.model.generate(**inputs, **self.generation_params)

        output = self.tokenizer.decode(generated_token_ids[0][len(inputs["input_ids"][0]) :])
        return output
