from telegram import Update
from telegram.ext import CallbackContext


class TelegramEvent:

    def __init__(self, update: Update, context: CallbackContext):
        """
        A convenient wrapper of received events.

        :param update: The telegram update that caused the event
        :param context: The telegram context tied to the user that caused the event
        """
        self.update: Update = update
        self.context: CallbackContext = context
        self.chat_id: int = update.effective_chat.id  # for convenience
        self.vars = context.chat_data  # for convenience

    def reply(self, text: str, **kwargs):
        self.context.bot.send_message(text, chat_id=self.update.effective_chat.id, **kwargs)


class TelegramFunctionBlueprint:

    def __call__(self, update: Update, context: CallbackContext) -> int or None:
        return self.logic(TelegramEvent(update, context))

    def __str__(self):
        return str(self.__dict__)

    def logic(self, event: TelegramEvent):
        raise NotImplemented


class TelegramUserError(Exception):
    pass
