from typing import List, Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from MateWrapper.globals import Globals


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


def get_keyboard(
        input_list: List[Dict[str, str] or List[Dict[str, str]]],
        add_back_button: bool = False,
        custom_back_text: str or None = None
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of dictionaries or lists of dictionaries

    :param input_list:
        the input list to transform into a keyboard.
        It should look something like this:
        [
            {
                "text": "button on a single line",
                "url": "https://github.com/SudoOmbro"
            },
            [
                {
                    "text": "left button",
                    "data": "callback1"
                },
                {
                    "text": "right button",
                    "data": "callback2"
                }
            ],
            ...
        ]
    :param add_back_button:
        if true automatically adds a back button
    :param custom_back_text:
        if set changes the back button's text
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
            back_button = InlineKeyboardButton(text=custom_back_text, callback_data=Globals.BACK_PATTERN)
        else:
            back_button = Globals.BACK_BUTTON
        keyboard_list.append([back_button])
    return InlineKeyboardMarkup(keyboard_list)


def get_keyboard_from_list(
        input_list: List,
        add_back_button: bool = False,
        custom_back_text: str or None = None,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of objects (that can be stringified).

    :param input_list: the list you wish to transform into a keyboard
    :param add_back_button: if true automatically adds a back button
    :param custom_back_text: if set changes the back button's text
    """
    new_list = [{"text": str(element), "data": str(element)} for element in input_list]
    return get_keyboard(new_list, add_back_button=add_back_button, custom_back_text=custom_back_text)
