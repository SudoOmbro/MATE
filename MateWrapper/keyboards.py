from typing import List, Dict, Callable, Union

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from MateWrapper.globals import Globals


def _default_get(element: object) -> str:
    return str(element)


def get_keyboard_from_list(
        input_list: List[object],
        base_keyboard_list: Union[List[List[InlineKeyboardButton]], None] = None,
        custom_text_generator: Union[Callable[[object], str], None] = None,
        custom_data_generator: Union[Callable[[object], str], None] = None,
        add_back_button: bool = False,
        custom_back_text: str or None = None,
        buttons_per_line: int = 1,
        urls: bool = False
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of objects (that can be stringified).

    :param List[object] input_list:
        the list you wish to transform into a keyboard.
    :param Union[List[List[InlineKeyboardButton]], None] base_keyboard_list:
        if passed all the new button will be appended to this base keyboard.
    :param Union[Callable[[object], str], None] custom_text_generator:
        the function that should be used to generate the
        text of the button, if not defined it will just do str(element).
    :param Union[Callable[[object], str], None] custom_data_generator:
        the function that should be used to generate the callback data
        (or the url, if the function is set to generate a urls keyboard) of the button.
    :param bool add_back_button:
        if true automatically adds a back button.
    :param str or None custom_back_text:
        if set changes the back button's text.
    :param int buttons_per_line:
        defines the maximum amount of buttons that will be in each line.
    :param bool urls:
        Defines if the data of the buttons should be callback data (default behaviour) or urls.
    """
    # get text & data generators
    text_generator = custom_text_generator if custom_text_generator else _default_get
    data_generator = custom_data_generator if custom_data_generator else _default_get
    # generate actual keyboard
    keyboard_list: List[List[InlineKeyboardButton]] = base_keyboard_list if base_keyboard_list else []
    if urls:
        for element in input_list:
            line: List[InlineKeyboardButton] = []
            for _ in range(buttons_per_line):
                line.append(InlineKeyboardButton(text=text_generator(element), url=data_generator(element)))
            keyboard_list.append(line)
    else:
        for element in input_list:
            line: List[InlineKeyboardButton] = []
            for _ in range(buttons_per_line):
                line.append(InlineKeyboardButton(text=text_generator(element), callback_data=data_generator(element)))
            keyboard_list.append(line)
    # add back button if wanted
    if add_back_button:
        if custom_back_text:
            keyboard_list.append([InlineKeyboardButton(text=custom_back_text, callback_data=Globals.BACK_PATTERN)])
        else:
            keyboard_list.append([InlineKeyboardButton(Globals.BACK_BUTTON)])
    return InlineKeyboardMarkup(keyboard_list)
