import logging
from typing import Callable

from telegram import Update
from telegram.ext import Updater, CallbackContext, Dispatcher, Handler, ConversationHandler

from MateWrapper.generics import TelegramUserError

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

log = logging.getLogger()
log.setLevel(logging.INFO)


def default_error_handler(update: Update, context: CallbackContext):
    """
    Built in error handler, just sends the given error message to the user if TelegramUserError and logs the
    Exception while notifying the user if it's not.
    """
    error: Exception = context.error
    if type(error) == TelegramUserError:
        # handle user error
        context.bot.send_message(text=str(error), chat_id=update.effective_chat.id)
    else:
        # handle program error
        context.bot.send_message(text="Critical failure", chat_id=update.effective_chat.id)
        log.exception(f"{error}\ndue to update: {update.to_dict()}\n")
        return ConversationHandler.END


class TelegramBot:
    """ class that wraps Updater and Dispatcher in a convenient way """

    def __init__(self, token: str, error_handler: Callable[[Update, CallbackContext], any] = None, name: str = ""):
        """
        :param token: the token necessary to run the bot, acquired through BotFather.
        :param error_handler: a custom error handler if you don't want to use the default one
        :param name: the name of this bot, currently unused.
        """
        self.updater: Updater = Updater(token=token, use_context=True)
        self.dispatcher: Dispatcher = self.updater.dispatcher
        if error_handler:
            # noinspection PyTypeChecker
            self.dispatcher.add_error_handler(error_handler)
        else:
            # noinspection PyTypeChecker
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
