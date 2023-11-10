# Digital twin backed

Project to copy conversation style using LLM model trainer on conversation in
instagram, telegram, vk, and own dataset.

Server for handling user requests, operating with conversation history.

Project consist of multiple-repos:

1. [TG_BOT github](https://github.com/zaaabik/digital-twin-tg-bot)
2. [LLM service](https://github.com/zaaabik/digital-twin-llm-backend)
3. [Data preprocessing and training](https://github.com/zaaabik/digital-twin)

How to run this repo:

```bash
docker pull zaaabik/digitaltwin-chat-bot:[TAG]
docker run -e CONTEXT_SIZE=8 -e DATABASE_CONNECTION_STRING=***MONGO_CONNECTION_STRING*** \
 -e HF_TOKEN=***HUGGING_FACE_TOKEN*** \
 -e LM_API_ADDRESS=***IP_ADRESS_LLM_SERVER*** \
 -e MODEL_NAME=***HF_MODEL_NAME*** \
 -e TEMPLATE_PATH=templates/chat_conversation_template.json \
 -e TABLE_NAME="telegram_users" \
 -p 52111:52111 zaaabik/digitaltwin-chat-bot:[TAG]
```

**TAGS: REST API, FastApi, MongoDB, GitHub Actions, Docker**
