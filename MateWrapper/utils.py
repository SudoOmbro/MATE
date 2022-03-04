from typing import Tuple, List, Dict

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, Handler

from MateWrapper.generics import TelegramFunctionBlueprint
from MateWrapper.prompts import Prompt

DEFAULT_BACK_BUTTON = InlineKeyboardButton(text="\U00002B05 Back", callback_data="__back__")


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

    def __call__(self, update: Update, context: CallbackContext):
        last_return_value = None
        for func in self.functions:
            ret = func(update, context)
            if ret is not None:
                last_return_value = ret
        if self.return_value:
            return last_return_value


def __is_button_valid(dictionary: Dict[str, str]):
    data = dictionary.get("data", None)
    url = dictionary.get("url", None)
    return (data is not None) or (url is not None)


def __get_button(dictionary: Dict[str, str]):
    text = dictionary.get("text", "")
    data = dictionary.get("data", None)
    url = dictionary.get("url", None)
    if data:
        return InlineKeyboardButton(text=text, callback_data=data)
    return InlineKeyboardButton(text=text, url=url)


def generate_keyboard(
        input_list: List[Dict[str, str] or List[Dict[str, str]]],
        add_back_button: bool = False,
        custom_back_text: str or None = None
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of dictionaries or lists of dictionaries

    :param input_list: the input list to transform into a keyboard
    :param add_back_button: if true automatically adds a back button
    :param custom_back_text: if set changes the back button's text
    """
    if (not input_list) and (not add_back_button):
        raise ValueError("The given list is empty or None!")
    keyboard_list: List[List[InlineKeyboardButton]] = []
    for element in input_list:
        if type(element) == list:
            line: List[InlineKeyboardButton] = []
            for sub_element in element:
                if __is_button_valid(sub_element):
                    line.append(__get_button(sub_element))
            keyboard_list.append(line)
        else:
            if __is_button_valid(element):
                keyboard_list.append([__get_button(element)])
    if add_back_button:
        if custom_back_text:
            back_button = InlineKeyboardButton(text=custom_back_text, callback_data="__back__")
        else:
            back_button = DEFAULT_BACK_BUTTON
        keyboard_list.append([back_button])
    return InlineKeyboardMarkup(keyboard_list)


def generate_keyboard_from_list(
        input_list: List,
        add_back_button: bool = False,
        custom_back_text: str or None = None,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of objects.

    :param input_list: the list you wish to transform into a keyboard
    :param add_back_button: if true automatically adds a back button
    :param custom_back_text: if set changes the back button's text
    """
    new_list = [{"text": str(element), "data": str(element)} for element in input_list]
    return generate_keyboard(new_list, add_back_button=add_back_button, custom_back_text=custom_back_text)


def MenuHandler(
        ph_map: Dict[str, TelegramFunctionBlueprint or Chain or callable],
        extra_handlers: List[Handler] or None = None,
        previous_menu: Prompt or None = None,
) -> List[Handler]:
    """
    generate a menu handler for all the buttons

    :param ph_map: the param-handler map
    :param extra_handlers: the extra handler to attach to the menu (like text or photo handler for example)
    :param previous_menu: if set automatically handles the "__back__" pattern to go to the given menu
    """
    if not ph_map:
        raise ValueError("No handler was passed!")
    handlers: List[Handler] = []
    for pattern in ph_map:
        handlers.append(CallbackQueryHandler(ph_map[pattern], pattern=pattern))
    if extra_handlers:
        handlers.extend(extra_handlers)
    if previous_menu is not None:
        handlers.append(CallbackQueryHandler(previous_menu, pattern="__back__"))
    return handlers
