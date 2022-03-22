from typing import List, Callable, Union, TypeVar

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from MateWrapper.globals import Globals


T = TypeVar("T")


def _default_get(element: object) -> str:
    return str(element)


def _add_back_button(
        keyboard_list: List[List[InlineKeyboardButton]],
        add_back_button: bool,
        custom_back_text: str or None
):
    if add_back_button:
        if custom_back_text:
            keyboard_list.append([InlineKeyboardButton(text=custom_back_text, callback_data=Globals.BACK_PATTERN)])
        else:
            keyboard_list.append([InlineKeyboardButton(Globals.BACK_BUTTON)])


def get_keyboard_from_list(
        input_list: List[T],
        pre_keyboard: Union[List[List[InlineKeyboardButton]], None] = None,
        post_keyboard: Union[List[List[InlineKeyboardButton]], None] = None,
        custom_text_generator: Union[Callable[[T], str], None] = None,
        custom_data_generator: Union[Callable[[T], str], None] = None,
        add_back_button: bool = False,
        custom_back_text: str or None = None,
        buttons_per_line: int = 1,
        urls: bool = False
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard from a list of objects (that can be stringified).

    :param List[T] input_list:
        the list you wish to transform into a keyboard.
    :param Union[List[List[InlineKeyboardButton]], None] pre_keyboard:
        if passed all new buttons will be appended to this base keyboard.
    :param Union[List[List[InlineKeyboardButton]], None] post_keyboard:
        if passed this keyboard will be appended to the generated keyboard.
    :param Union[Callable[[T], str], None] custom_text_generator:
        the function that should be used to generate the
        text of the button, if not defined it will just do str(element).
    :param Union[Callable[[T], str], None] custom_data_generator:
        the function that should be used to generate the callback data
        (or the url, if the function is set to generate a url keyboard) of the button.
    :param bool add_back_button:
        if true automatically adds a back button at the bottom of the keyboard.
    :param str or None custom_back_text:
        if set changes the back button's text.
    :param int buttons_per_line:
        defines the maximum amount of buttons that will be in each line.
    :param bool urls:
        Defines if the data of the buttons should be callback data (default behaviour) or urls.
    :return: InlineKeyboardMarkup
    """
    # get text & data generators
    text_generator = custom_text_generator if custom_text_generator else _default_get
    data_generator = custom_data_generator if custom_data_generator else _default_get
    # generate actual keyboard
    keyboard_list: List[List[InlineKeyboardButton]] = pre_keyboard if pre_keyboard else []
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
    # add post keyboard
    if post_keyboard:
        keyboard_list.extend(post_keyboard)
    # add back button if wanted
    _add_back_button(keyboard_list, add_back_button, custom_back_text)
    return InlineKeyboardMarkup(keyboard_list)


def get_keyboard_custom_row(
        input_list: List[T],
        row_generator_function: Callable[[T], List[InlineKeyboardButton]],
        pre_keyboard: Union[List[List[InlineKeyboardButton]], None] = None,
        post_keyboard: Union[List[List[InlineKeyboardButton]], None] = None,
        add_back_button: bool = False,
        custom_back_text: str or None = None
) -> InlineKeyboardMarkup:
    """
    Generates a custom keyboard from a given list and a given row_generator_function.

    :param List[T] input_list:
        the list you wish to transform into a keyboard.
    :param Callable[[T], List[InlineKeyboardButton]] row_generator_function:
        The function to use to generate a row of the keyboard given an element of the list.
    :param Union[List[List[InlineKeyboardButton]], None] pre_keyboard:
        if passed all new buttons will be appended to this base keyboard.
    :param Union[List[List[InlineKeyboardButton]], None] post_keyboard:
        if passed this keyboard will be appended to the generated keyboard.
    :param bool add_back_button:
        if true automatically adds a back button at the bottom of the keyboard.
    :param str or None custom_back_text:
        if set changes the back button's text.
    :return: InlineKeyboardMarkup
    """
    # init base keyboard
    keyboard_list: List[List[InlineKeyboardButton]] = pre_keyboard if pre_keyboard else []
    # generate actual keyboard
    for element in input_list:
        keyboard_list.append(row_generator_function(element))
    # add post keyboard
    if post_keyboard:
        keyboard_list.extend(post_keyboard)
    # add back button if wanted
    _add_back_button(keyboard_list, add_back_button, custom_back_text)
    return InlineKeyboardMarkup(keyboard_list)

