from typing import Dict

from telegram.ext import CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

from MateWrapper.generics import TelegramFunctionBlueprint


class ButtonHandler(CallbackQueryHandler):
    """ Handles Button inputs, it's just an alias for CallbackQueryHandler """
    pass


class TextHandler(MessageHandler):
    """ Handles text messages, wraps MessageHandler """

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.text & (~Filters.command), callback, **kwargs)


class PhotoHandler(MessageHandler):
    """ Handles Photo messages, wraps MessageHandler """

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.photo, callback, **kwargs)
