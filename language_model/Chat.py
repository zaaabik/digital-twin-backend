import json

from transformers import PreTrainedTokenizer

DEFAULT_MESSAGE_TEMPLATE = "<s>{role}\n{content}</s>\n"
DEFAULT_SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."
DEFAULT_START_TOKEN_ID = 1
DEFAULT_END_TOKEN_ID = 2
DEFAULT_BOT_TOKEN_ID = 9225


class Conversation:
    r"""Class for storing conversation and format it for LLM model."""

    def __init__(
        self,
        message_template=DEFAULT_MESSAGE_TEMPLATE,
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        role_mapping=None,
        start_token_id=DEFAULT_START_TOKEN_ID,
        end_token_id=DEFAULT_END_TOKEN_ID,
        bot_token_id=DEFAULT_BOT_TOKEN_ID,
    ):
        self.message_template = message_template
        self.role_mapping = role_mapping or {}
        self.start_token_id = start_token_id
        self.end_token_id = end_token_id
        self.bot_token_id = bot_token_id
        self.messages = [{"role": "system", "content": system_prompt}]

    def get_end_token_id(self):
        r"""Return end of generation token id."""
        return self.end_token_id

    def get_start_token_id(self):
        r"""Return start of generation token id."""
        return self.start_token_id

    def get_bot_token_id(self):
        r"""Return bot token id."""
        return self.bot_token_id

    def add_user_message(self, message: str):
        r"""Add new user message to previous messages."""
        self.messages.append({"role": "user", "content": message})

    def add_bot_message(self, message: str):
        r"""Add bot message to previous messages."""
        self.messages.append({"role": "bot", "content": message})

    def count_tokens(self, tokenizer: PreTrainedTokenizer, messages: list[dict]):
        r"""Count tokens after tokenization."""
        final_text = ""
        for message in messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        tokens = tokenizer([final_text])["input_ids"][0]
        return len(tokens)

    def shrink(self, tokenizer: PreTrainedTokenizer, messages: list[dict], max_tokens: int):
        system_message = messages[0]
        other_messages = messages[1:]
        while self.count_tokens(tokenizer, [system_message] + other_messages) > max_tokens:
            other_messages = other_messages[2:]
        return [system_message] + other_messages

    def get_prompt(self, tokenizer: PreTrainedTokenizer, max_tokens: int = 512):
        r"""Return text for passing to LLM."""
        final_text = ""
        messages = self.messages
        if max_tokens is not None:
            messages = self.shrink(tokenizer, messages, max_tokens)

        for message in messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        return final_text.strip()

    def get_prompt_for_generate(self, tokenizer, max_tokens: int = 512):
        r"""Return text for passing to LLM with prefix for future generation."""
        final_text = ""
        messages = self.messages
        if max_tokens is not None:
            messages = self.shrink(tokenizer, messages, max_tokens)

        for message in messages:
            message_text = self.message_template.format(**message)
            final_text += message_text
        final_text += tokenizer.decode([self.start_token_id, self.bot_token_id])
        return final_text.strip()

    @classmethod
    def from_template(cls, file_name: str):
        r"""Init class from json template."""
        with open(file_name, encoding="UTF-8") as r:
            template = json.load(r)
        return Conversation(**template)

    def expand(self, messages: list[dict]):
        r"""Add multiple messages."""
        if len(messages) and (messages[0]["role"] == "system"):
            self.messages = []

        for message in messages:
            self.messages.append(
                {
                    "role": self.role_mapping.get(message["role"], message["role"]),
                    "content": message["content"],
                }
            )
