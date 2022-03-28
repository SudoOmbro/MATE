from types import FunctionType
from typing import Tuple, Callable

from telegram import Update
from telegram.ext import CallbackContext


class TelegramEvent:
    """ A convenient wrapper of received events. Automatically instanced by the wrapper. """

    def __init__(self, update: Update, context: CallbackContext):
        """
        :param Update update: The telegram update that caused the event
        :param CallbackContext context: The telegram context tied to the user that caused the event
        """
        self.update: Update = update
        self.context: CallbackContext = context
        self.chat_id: int = update.effective_chat.id  # for convenience
        self.vars = context.chat_data  # for convenience

    def reply(self, text: str, **kwargs):
        """ send message to the user that generated this event. Supports all kwargs of send_message. """
        self.context.bot.send_message(text, chat_id=self.update.effective_chat.id, **kwargs)


class TelegramFunctionBlueprint:
    """
    The generic Telegram Function class that needs to be implemented.

    This class is callable.
    """

    def __call__(self, update: Update, context: CallbackContext) -> int or None:
        return self.logic(TelegramEvent(update, context))

    def __str__(self):
        return str(self.__dict__)

    def logic(self, event: TelegramEvent) -> object or None:
        """
        How this method is implemented determines what the function is going to do.
        What this method returns defines the next state that the menu needs to be in.
        """
        raise NotImplemented


class Chain:
    """
    Used to call multiple functions from a single handle, useful to avoid creating custom functions for most
    interactions with the Bot.
    Chains can be Nested in other chains to create subroutines.

    This class is callable.
    """

    def __init__(
            self,
            *args: Callable[[Update, CallbackContext], object],
            next_state: object or None = None
    ):
        """
        :param Callable[[Update, CallbackContext], object] args:
             a tuple containing the functions that will be called,
             starting from the first and finishing with the last,
             returning the last non-None value if return_value is not defined.
        :param object or None next_state:
             if defined then the chain will return the given value,
             if not it will return the last non-None value.
             By default, it's not defined, the last non-None value is returned.
        """
        self.functions: Tuple = args
        self.next_state: object or None = next_state

    def __call__(self, update: Update, context: CallbackContext):
        last_return_value = None
        for func in self.functions:
            ret = func(update, context)
            last_return_value = ret if ret is not None else last_return_value
        if self.next_state:
            return self.next_state
        return last_return_value


class TelegramUserError(Exception):
    """
    This exception is raised if the wrapper detects an error from a user,
    for example when the validation regex in GetText does not match the input.

    It's handled automatically by the default error handler, but you can implement your own handler.
    """
