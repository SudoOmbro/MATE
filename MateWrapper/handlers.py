from typing import Dict

from telegram.ext import CallbackQueryHandler, MessageHandler, Filters, ConversationHandler

from MateWrapper.generics import TelegramFunctionBlueprint


END_CONVERSATION = ConversationHandler.END


class Conversation(ConversationHandler):
    pass


class ButtonHandler(CallbackQueryHandler):
    pass


class TextHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.text & (~Filters.command), callback, **kwargs)


class PhotoHandler(MessageHandler):

    def __init__(self, callback: callable or TelegramFunctionBlueprint, **kwargs):
        super().__init__(Filters.photo, callback, **kwargs)
