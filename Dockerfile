FROM python:3.9
COPY . /app
WORKDIR /app
ARG HF_TOKEN
ARG MODEL_NAME
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN huggingface-cli download --token=${HF_TOKEN} ${MODEL_NAME}
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
