from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ConversationHandler

from MateWrapper.prompts import Prompt


class Globals:
    """
    Contains a bunch of useful shortcuts and globals used across the wrapper.
    """

    # Patterns
    BACK_PATTERN = "__back__"
    """ 
    The callback pattern globally used by the back button, 
    assign this as callback data to a custom button to give it the function of going to the previous panel.
    """
    CLOSE_MENU = "__end__"

    # Buttons
    BACK_BUTTON = InlineKeyboardButton(text="\U00002B05 Back", callback_data=BACK_PATTERN)
    """
    The default back button used by the wrapper.
    """

    # Keyboards
    BACK_KEYBOARD = InlineKeyboardMarkup([[BACK_BUTTON]])
    """
    A keyboard only containing the back button.
    """

    # Prompts
    CONVERSATION_END_PROMPT = Prompt(
        "Conversation ended.",
        next_state=ConversationHandler.END,
        delete_last_message=True
    )
    """
    The default prompt shown by the wrapper when exiting a menu
    """

    # Placeholder entry point
    ENTRY_POINT = lambda u, c: None
    """
    A placeholder function that does nothing that will be automatically 
    replaced by the wrapper with the prompt associated with the defined main panel.
    
    This process happens at init time so it has no impact on runtime performance.
    """

    # Handlers
    END_HANDLER = CallbackQueryHandler(
        CONVERSATION_END_PROMPT,
        pattern=BACK_PATTERN
    )
    """ An handler for BACK_PATTERN that will end the conversation (close the menu) """
