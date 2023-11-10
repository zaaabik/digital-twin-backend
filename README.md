# Digital twin backed

Server for handling user requests, operating with conversation history, and
use LLM service to generate responses.

**TAGS: REST API, FastApi, MongoDB, GitHub Actions, Docker**

```bash
docker pull zaaabik/digitaltwin-chat-bot:[TAG]
docker run -e CONTEXT_SIZE=8 -e DATABASE_CONNECTION_STRING=***MONGO_CONNECTION_STRING*** \
 -e HF_TOKEN=***HUGGING_FACE_TOKEN*** \
 -e LM_API_ADDRESS=***IP_ADRESS_LLM_SERVER*** \
 -e MODEL_NAME=***HF_MODEL_NAME*** \
 -e TEMPLATE_PATH=templates/chat_conversation_template.json \
 -p 52111:52111 zaaabik/digitaltwin-chat-bot:[TAG]
```
