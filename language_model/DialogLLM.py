from huggingface_hub import login

from language_model.model import LanguageModel
from transformers import AutoTokenizer, AutoModelWithLMHead


class DialogLLM(LanguageModel):
    def __init__(self, hf_token: str, model_name: str):
        login(hf_token)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name, return_token_type_ids=False)
        self.model = AutoModelWithLMHead.from_pretrained(model_name)

        self.generation_params = dict(
            top_k=25,
            top_p=0.90,
            num_beams=2,
            num_return_sequences=1,
            do_sample=True,
            no_repeat_ngram_size=2,
            temperature=1.2,
            repetition_penalty=1.2,
            length_penalty=-15.,
            eos_token_id=50257,
            max_new_tokens=60,
            sequence_bias={
                (21,): -10.0,
                self.get_tokens_as_tuple('У тебя как?'): -10.,
                self.get_tokens_as_tuple('Че делаешь сегодня?'): -10.,
                self.get_tokens_as_tuple('чувствуешь'): -10.,
                self.get_tokens_as_tuple('Живой?'): -10.,
                self.get_tokens_as_tuple('ты как'): -10.,
                self.get_tokens_as_tuple('Ты как'): -10.,
                self.get_tokens_as_tuple('Аудиозапись'): -100.,
                self.get_tokens_as_tuple('А ты?'): -10.,
                self.get_tokens_as_tuple('как дела'): -10.,
        }
        )

    def get_tokens_as_tuple(self, word):
        return tuple(self.tokenizer([word], add_special_tokens=False).input_ids[0])

    def generate(self, context) -> str:
        inputs = self.tokenizer(context, return_tensors='pt')
        generated_token_ids = self.model.generate(
            **inputs,
            **self.generation_params
        )

        output = self.tokenizer.decode(generated_token_ids[0][len(inputs['input_ids'][0]):])
        return output
