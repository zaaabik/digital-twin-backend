FROM python:3.9
COPY . /app
WORKDIR /app
ARG HF_TOKEN
ARG MODEL_NAME
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN huggingface-cli download --token=${HF_TOKEN} zaaabik/digital_twin_medium_tg_vk_context_len_8_filtered_both_best_model_metric
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
