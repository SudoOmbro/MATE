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
    return f"__b{current_id}__"


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
    """ generic keyboard button class to implement """

    def __init__(self, text: str):
        if not text:
            raise ValueError("A button needs some text in it")
        self.text: str = text
        self.handle: str = _get_button_handle()

    def setup(self, parent_menu: "Menu", parent_panel: "Panel", last_state: int):
        # implement if the button needs the menu's context to initialize itself
        return last_state

    def callback_handler(self) -> callable or None:
        return None

    def keyboard_button(self) -> InlineKeyboardButton:
        """ by default generates the button with its handle as callback data """
        return InlineKeyboardButton(self.text, callback_data=self.handle)


class GotoButton(Button):
    """ button that allows for Panel changing """
    # TODO
    pass


class UrlButton(Button):
    """ button that redirects the user to the specified url when clicked """

    def __init__(self, text: str, url: str):
        super().__init__(text)
        if not url:
            raise ValueError("The url cannot be empty")
        self.url = url

    def keyboard_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(self.text, url=self.url)


class FuncButton(Button):
    """ button that executes a function when clicked """

    def __init__(self, text: str, function: callable):
        super().__init__(text)
        if not function:
            raise ValueError("The function cannot be None")
        self.func = function

    def callback_handler(self) -> callable or None:
        return self.func


class InputButton(FuncButton):
    """ button that makes getting inputs from users a lot easier by automating callback and state handling """

    def __init__(self, text: str, prompt: Prompt, function: callable):
        super().__init__(text, function)
        self.prompt: Prompt = prompt
        self.new_state: int = 0

    def setup(self, parent_menu: "Menu", parent_panel: "Panel", current_state: int):
        self.new_state: int = current_state + 1
        self.func = Chain(self.func, next_state=current_state)
        return self.new_state

    def callback_handler(self) -> callable or None:
        return Chain(self.prompt, next_state=self.new_state)


class Panel:
    """
    A menu view, basically a prompt with a keyboard (if needed)

    Parameters:

    prompt_text (str):
        The text that will be sent when this panel is shown,
        supports all the same formatting options as the Panel object.
    buttons (List[Button or List[Button]]):
        The list of Button objects (or of List[Button]) that will define the functionality of this panel.
    back_to (str):
        The name of the Panel to go back to. If "__end__" the back button will close the menu.
    extra_handlers (List[callable]):
        A list of extra handlers that can do extra stuff, like read text inputs and stuff like that.
    """

    def __init__(
            self,
            prompt_text: str,
            buttons: List[Button or List[Button]],
            back_to: str,
            extra_handlers: List[callable]
    ):
        self.prompt_text = prompt_text
        self.buttons = buttons
        self.back_to = back_to
        self.extra_handlers = extra_handlers

    def keyboard(self) -> InlineKeyboardMarkup:
        """ returns a keyboard object that the base wrapper can use """
        keyboard_list: List[List[InlineKeyboardButton]] = []
        for button in self.buttons:
            # TODO
            pass
        return InlineKeyboardMarkup(keyboard_list)


class Menu(ConversationHandler):
    """
    A menu, container for one or more (usually more) panels

    Parameters:

    entry_points (List[Handler]):
        The list of handlers that will activate this menu from the "main" state.
    panels (Dict[str, Panel]):
        A dictionary containing the name-panel pair.
    main_panel (str):
        Defines which panel to show when first entering the menu
    fallbacks (List[Handler]):
        A list of extra handlers valid in the entire menu, useful for example for commands.
    """

    def __init__(
            self,
            entry_points: List[Handler],
            panels: Dict[str, Panel],
            main_panel: str,
            fallbacks: List[Handler]
    ):
        self.submenus = panels
        self.main_panel = main_panel
        super().__init__(entry_points, self.__compile(panels, main_panel), fallbacks)

    def __compile(self, panels: Dict[str, Panel], main_panel: str) -> Dict[int, List[Handler]]:
        # TODO compile panels into states with handlers
        pass
