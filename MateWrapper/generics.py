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
        raise NotImplemented


class Chain:
    """
    Used to call multiple functions from a single handle, useful to avoid creating custom functions for most
    interactions with the Bot.
    Chains can be Nested in other chains to create subroutines

    Parameters:

    args (Tuple[callable]):
        a tuple containing the functions that will be called,
        starting from the first and finishing with the last,
        returning the last non-None value if return_value is not defined.
    next_state (int or None):
        if defined then the chain will return the given value,
        if not it will return the last non-None value.
        By default, it's not defined, the last non-None value is returned.
    """

    def __init__(self, *args: TelegramFunctionBlueprint or callable, next_state: object or None = None):
        self.functions: Tuple = args
        self.next_state: bool = next_state

    def __call__(self, update: Update, context: CallbackContext):
        last_return_value = None
        for func in self.functions:
            ret = func(update, context)
            if ret is not None:
                last_return_value = ret
        if self.next_state:
            return self.next_state
        return last_return_value


class TelegramUserError(Exception):
    pass
