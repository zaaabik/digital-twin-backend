from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler

from database.Interface import DataBase
from language_model.model import LanguageModel
from utils.logger import get_pylogger

log = get_pylogger(__name__)


class TgBot:
    def __init__(self, token: str, database: DataBase, lm: LanguageModel, context_size: int = 8):
        self.app = ApplicationBuilder().token(token).build()
        self.database = database
        self.lm = lm
        self.context_size = context_size

    def process_context(self, full_context):
        return full_context[-self.context_size:]

    async def message_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_user_id: str = str(update.effective_user.id)
        username: str = str(update.effective_user.username)
        text: str = update.message.text
        text_with_prefix = f'@@ВТОРОЙ@@ {text}'

        self.database.create_user_if_not_exists(telegram_user_id=telegram_user_id, username=username)
        log.info('create_user_if_not_exists')

        self.database.update_user_text(telegram_user_id=telegram_user_id, text=text_with_prefix)
        log.info('update_user_text')

        user = self.database.get_user(telegram_user_id=telegram_user_id)
        full_context = user.context
        context = self.process_context(full_context)
        str_context = ' '.join(context)
        context_for_generation = f'{str_context} @@ПЕРВЫЙ@@'
        log.info(f'Context for model generation: {context_for_generation}')

        model_response = self.lm.generate(context_for_generation)
        pure_response: str = model_response[:model_response.find('@@ВТОРОЙ@@')]
        pure_response = pure_response.rstrip(' ')

        model_response_to_db = f'@@ПЕРВЫЙ@@ {pure_response}'
        self.database.update_user_text(telegram_user_id=telegram_user_id, text=model_response_to_db)
        log.info('update_user_text model answer')

        await update.message.reply_text(pure_response)

    async def remove_user_callback(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        telegram_user_id: str = str(update.effective_user.id)
        self.database.remove_user(telegram_user_id=telegram_user_id)
        log.info(f'Remove user {telegram_user_id}')

        await update.message.reply_text(f'User {telegram_user_id} removed')

    def run(self):
        self.app.add_handler(CommandHandler(
            command='remove',
            callback=self.remove_user_callback
        ))
        self.app.add_handler(MessageHandler(
            filters=None,
            callback=self.message_callback
        ))
        self.app.run_polling()