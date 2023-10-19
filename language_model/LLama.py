import torch
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from language_model.model import LanguageModel


class LLama(LanguageModel):
    r"""Class for generation answers for bot using LLM from huggingface repos."""

    def __init__(self, hf_token: str, model_name: str):
        r"""
        Init class for generation answers for bot
        Args:
            hf_token: hugging face token using for download model
            model_name: LLM model name
        """
        login(hf_token)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, return_token_type_ids=False)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.bfloat16, device_map="auto"
        )

        self.generation_config = GenerationConfig(
            **{
                "bos_token_id": 1,
                "eos_token_id": 2,
                "max_new_tokens": 2048,
                "no_repeat_ngram_size": 20,
                "num_beams": 5,
                "num_return_sequences": 5,
                "pad_token_id": 0,
                "length_penalty": +5.0,
                "sequence_bias": {
                    self.get_tokens_as_tuple("http:"): -10.0,
                    self.get_tokens_as_tuple("🇷🇺"): -10.0,
                    self.get_tokens_as_tuple("🧐"): -10.0,
                },
            }
        )

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

        with torch.no_grad():
            data = self.tokenizer(context, return_tensors="pt")
            data = {k: v.to(self.model.device) for k, v in data.items()}
            output_ids = self.model.generate(**data, generation_config=self.generation_config)
            output_ids = [
                self.tokenizer.decode(o[len(data["input_ids"][0]) :]) for o in output_ids
            ]
            outputs = output_ids

            smallest_id = -1
            smallest_value = float("+inf")
            for idx, output in enumerate(outputs):
                curr_count = output.count("<unk>")
                if curr_count < smallest_value:
                    smallest_id = idx
                    smallest_value = curr_count
            output = outputs[smallest_id]
            output = output[: output.find("\n</s>")]

            return output
