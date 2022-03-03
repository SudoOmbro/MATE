from typing import Tuple

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
        pass


class Chain:

    def __init__(self, *args: TelegramFunctionBlueprint or callable, return_value: bool = True):
        """
        Used to call multiple functions from a single handle, useful to avoid creating custom functions for most
        interactions with the Bot.
        Chains can be Nested in other chains to create subroutines.

        :param args:
            a tuple containing the functions that will be called,
            starting from the first and finishing with the last,
            returning the last non null value if return_value is True.
        :param return_value:
            if True returns the last returned non-None value, if False it doesn't return anything. By default it's true
        """
        self.functions: Tuple = args
        self.return_value: bool = return_value
        # TODO(?) add a Chain subclass used for authentication

    def __call__(self, update: Update, context: CallbackContext):
        last_return_value = None
        for func in self.functions:
            ret = func(update, context)
            if ret is not None:
                last_return_value = ret
        if self.return_value:
            return last_return_value


class TelegramUserError(Exception):
    pass
