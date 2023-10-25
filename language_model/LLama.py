import torch
from huggingface_hub import login
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from language_model.model import LanguageModel


class LLama(LanguageModel):
    r"""Class for generation answers for bot using LLM from huggingface repos."""

    def __init__(
        self,
        hf_token: str,
        model_name: str,
        use_8_bit: bool = False,
        use_flash_attention_2: bool = False,
    ):
        r"""
        Init class for generation answers for bot
        Args:
            hf_token: hugging face token using for download model
            model_name: LLM model name
        """
        login(hf_token)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            use_flash_attention_2=use_flash_attention_2,
            load_in_8bit=use_8_bit,
        )

        self.generation_config = GenerationConfig.from_pretrained(
            model_name, min_new_tokens=2, num_return_sequences=1
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
                self.tokenizer.decode(
                    o[len(data["input_ids"][0]) :], skip_special_tokens=True
                ).strip()
                for o in output_ids
            ]
            outputs = output_ids

            return outputs[0]
