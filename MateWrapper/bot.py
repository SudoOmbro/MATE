import logging

from telegram.ext import Updater, CallbackContext, Dispatcher, Handler

from MateWrapper.generics import TelegramUserError

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

log = logging.getLogger()
log.setLevel(logging.INFO)


def default_error_handler(update, context: CallbackContext):
    error: Exception = context.error
    if type(error) == TelegramUserError:
        # handle user error
        context.bot.send_message(text=str(error), chat_id=update.effective_chat.id)
    else:
        # handle program error
        log.error(f"{error}\ndue to update: {update.to_dict()}\n")


class TelegramBot:

    def __init__(self, token: str, error_handler: callable = None, name: str = ""):
        self.updater: Updater = Updater(token=token, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        if error_handler:
            self.dispatcher.add_error_handler(error_handler)
        else:
            self.dispatcher.add_error_handler(default_error_handler)
        self.name = name

    def add_handler(self, handler: Handler):
        self.dispatcher.add_handler(handler)

    def start(self):
        log.info(f"Bot {self.name} started")
        self.updater.start_polling()

    def stop(self):
        log.info(f"Bot {self.name} stopped")
        self.updater.stop()

    def start_and_idle(self):
        self.start()
        self.updater.idle()
        self.updater.stop()
