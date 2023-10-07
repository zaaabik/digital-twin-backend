import logging
import os

from language_model.DialogLLM import DialogLLM
from language_model.model import LanguageModel
from message_bot.tg_bot import TgBot
from database.Interface import DataBase
from database.mongo import MongoDataBase

from utils.logger import get_pylogger
log = get_pylogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    mongo_user_name = os.getenv('MONGO_USER_NAME')
    mongo_user_password = os.getenv('MONGO_USER_PASSWORD')
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    HF_TOKEN = os.getenv('HF_TOKEN')
    MODEL_NAME = 'zaaabik/digital_twin_medium_tg_vk_context_len_8_filtered_both_best_model_metric'
    # MODEL_NAME = 'zaaabik/digital_twin_tg'

    connection_string = f'mongodb+srv://{mongo_user_name}:{mongo_user_password}' \
                        '@cluster0.3xrjcun.mongodb.net/?retryWrites=true&w=majority'
    TABLE_NAME = 'users'
    DATABASE_NAME = 'chat'

    log.info('Open database connection')
    database: DataBase = MongoDataBase(
        connection_string=connection_string,
        database_name=DATABASE_NAME,
        table_name=TABLE_NAME
    )

    log.info('Building LM model')
    lm: LanguageModel = DialogLLM(
        hf_token=HF_TOKEN,
        model_name=MODEL_NAME
    )

    log.info('Init bot')
    bot: TgBot = TgBot(TELEGRAM_BOT_TOKEN, database=database, lm=lm)
    log.info('Run bot')
    bot.run()
