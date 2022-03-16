from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler

from MateWrapper.prompts import Prompt


class Globals:

    # Patterns
    BACK_PATTERN = "__back__"
    END_PATTERN = "__end__"

    # Buttons
    BACK_BUTTON = InlineKeyboardButton(text="\U00002B05 Back", callback_data=BACK_PATTERN)

    # Keyboards
    BACK_KEYBOARD = InlineKeyboardMarkup([[BACK_BUTTON]])

    # Prompts
    CONVERSATION_END_PROMPT = Prompt(
        "Conversation ended.",
        next_state=ConversationHandler.END,
        delete_last_message=True
    )

    # Placeholder entry point
    ENTRY_POINT = lambda u, c: None

    # Handlers
    END_HANDLER = CallbackQueryHandler(
        CONVERSATION_END_PROMPT,
        pattern=BACK_PATTERN
    )
