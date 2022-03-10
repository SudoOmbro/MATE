from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Handler, CallbackQueryHandler, ConversationHandler

from MateWrapper.generics import TelegramFunctionBlueprint
from MateWrapper.prompts import Prompt
from MateWrapper.generics import Chain


__BUTTON_COUNTER: int = 0


def _get_button_handle() -> str:
    global __BUTTON_COUNTER
    current_id = __BUTTON_COUNTER
    __BUTTON_COUNTER += 1
    return f"__b{current_id}"


def get_menu_handler(
        ph_map: Dict[str, TelegramFunctionBlueprint or Chain or callable],
        extra_handlers: List[Handler] or None = None,
        previous_menu: Prompt or None = None,
) -> List[Handler]:
    """
    functions that generates a handler for a single state

    :param ph_map:
        the pattern-handler map,
        it should look something like this:

        {
            "pattern1": callback1,
            "pattern2": callback2,
            ...
        }
    :param extra_handlers:
        the extra handler to attach to the menu (like text or photo handler for example)
    :param previous_menu:
        if set automatically handles the "__back__" pattern to go to the given menu
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


class Button:

    def __init__(self, text: str):
        if not text:
            raise ValueError("A button needs some text in it")
        self.text: str = text
        self.handle: str = _get_button_handle()

    def setup(self, parent_menu: "Menu", parent_submenu: "Panel"):
        # implement if the button needs the menu's context to initialize itself
        pass

    def callback_handler(self) -> callable or None:
        return None

    def keyboard_button(self) -> InlineKeyboardButton:
        raise NotImplemented()


class UrlButton(Button):

    def __init__(self, text: str, url: str):
        super().__init__(text)
        if not url:
            raise ValueError("The url cannot be empty")
        self.url = url

    def keyboard_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(self.text, url=self.url)


class FuncButton(Button):

    def __init__(self, text: str, function: callable):
        super().__init__(text)
        if not function:
            raise ValueError("The function cannot be None")
        self.func = function

    def keyboard_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(self.text, callback_data=self.handle)

    def callback_handler(self) -> callable or None:
        return self.func


class Panel:

    def __init__(self, prompt: Prompt, buttons: List[Button or List[Button]], back_to: str):
        self.prompt = prompt
        self.buttons = buttons
        self.back_to = back_to

    def keyboard(self) -> InlineKeyboardMarkup:
        keyboard_list: List[List[InlineKeyboardButton]] = []
        # TODO
        return InlineKeyboardMarkup(keyboard_list)


class Menu:

    def __init__(
            self,
            entry_points: List[Handler],
            submenus: Dict[str, Panel],
            fallbacks: List[Handler] or None = None
    ):
        self.entry_points = entry_points,
        self.submenus = submenus
        self.fallbacks = fallbacks

    def get_conversation(self) -> ConversationHandler:
        return ConversationHandler(
            entry_points=self.entry_points,
            states={},  # TODO
            fallbacks=self.fallbacks
        )
