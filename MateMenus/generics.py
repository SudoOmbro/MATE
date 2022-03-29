from functools import cache
from typing import List, Dict, Callable

from telegram import InlineKeyboardButton, Update
from telegram.ext import ConversationHandler, Handler, CallbackQueryHandler, CallbackContext

from MateWrapper.generics import Chain, TelegramEvent, TelegramUserError
from MateWrapper.globals import Globals
from MateWrapper.prompts import Prompt

__BUTTON_COUNTER: int = 0


def _get_button_handle() -> str:
    """ generate a unique callback pattern for each button """
    global __BUTTON_COUNTER
    current_id = __BUTTON_COUNTER
    __BUTTON_COUNTER += 1
    return f"__b{current_id}__"


@cache
def get_back_button_handler(current_panel: "GenericPanel") -> CallbackQueryHandler:
    """
    returns a Handler for BACK_PATTERN that returns the user to current_panel

    :param GenericPanel current_panel: the destination panel
    :return: a CallbackQueryHandler for BACK_PATTERN that returns the user to current_panel
    """
    return CallbackQueryHandler(current_panel.prompt, pattern=Globals.BACK_PATTERN)


class MenuContext:
    """ Private class used by Menus to compile buttons and panels """

    def __init__(self, current_menu: "Menu", current_panel: "GenericPanel", panels: Dict[object, "GenericPanel"]):
        self.current_menu = current_menu
        self.current_panel = current_panel
        self.panels = panels


class Button:
    """ generic keyboard button class to implement """

    def __init__(self, text: str, custom_handle: str or None = None):
        """
        sets the buttons text & generates a unique handle (callback pattern) for this button.

        :param str text:
            the text that will be shown on the button (Long texts will be shortened).
        :param str or None custom_handle:
            Sets a custom handle for the button instead of autogenerating it.
        """
        if not text:
            raise ValueError("A button needs some text in it")
        self.text: str = text
        self.handle: str = custom_handle if custom_handle else _get_button_handle()

    def compile(self, context: MenuContext):
        """
        This function should only be called ad init time by a Menu object.

        Compiles the button given the menu context, useful if the button needs some context info to function,
        like for example buttons that change panel need to access the destination panel's prompt.

        By default, it does nothing and isn't mandatory to implement.
        """
        pass

    def get_next_state_handlers(self) -> Handler or List[Handler] or None:
        """
        Used mainly by input buttons. If this function returns a Handler or a list of Handlers then it tells the
        menu that this button spawns a sub-panel with its own handlers that then immediately returns to the
        current panel.
        """
        return None

    def get_handler(self) -> Handler or None:
        """ returns this buttons Handlers """
        return None

    def get_keyboard_button(self) -> InlineKeyboardButton:
        """ by default generates the button with its handle as callback data """
        return InlineKeyboardButton(self.text, callback_data=self.handle)


class GenericPanel:
    """ Panel prototype that needs to be implemented """

    prompt: Prompt
    """ the prompt to set with set_prompt """

    def set_prompt(self, current_state: object):
        """ This sets the prompt tied to the panel that needs to be shown when switching to it. """
        raise NotImplemented

    def get_handlers(self, context: MenuContext) -> List[Handler]:
        """ This is used by the menu object to compile panels into handlers. """
        raise NotImplemented


class Menu(ConversationHandler):
    """
    A menu, container for one or more (usually more) panels.

    At init time it automatically "compiles" the panels into handlers & callback handlers to ensure maximum runtime
    performance while retaining the simplicity of the wrapper.
    """

    def __init__(
            self,
            entry_points: List[Handler],
            panels: Dict[object, GenericPanel],
            main_panel: object,
            fallbacks: List[Handler]
    ):
        """
        :param entry_points:
            The list of handlers that will activate this menu from the "main" state.
        :param panels:
            A dictionary containing the name-panel pair.
        :param main_panel:
            Defines which panel to show when first entering the menu
        :param fallbacks:
            A list of extra handlers valid in the entire menu, useful for example for commands.
        """
        super().__init__(
            entry_points,
            {},
            fallbacks
        )
        self.__compile(panels)
        if main_panel not in panels:
            raise ValueError(f"The specified main panel '{main_panel}' isn't defined")
        for handler in entry_points:
            if type(handler.callback) == Chain:
                if Globals.ENTRY_POINT in handler.callback.functions:
                    handler.callback = Chain(handler.callback, panels[main_panel].prompt)
            elif handler.callback == Globals.ENTRY_POINT:
                handler.callback = panels[main_panel].prompt

    def __compile(self, panels: Dict[object, GenericPanel]) -> Dict[int, List[Handler]]:
        result: Dict[int, List[Handler]] = {}
        # set panel prompts before compiling buttons, necessary to make switching panels easier
        for panel_name in panels:
            panels[panel_name].set_prompt(panel_name)
        # compile panels to make all the handlers functional
        for panel_name in panels:
            self.states[panel_name] = panels[panel_name].get_handlers(MenuContext(self, panels[panel_name], panels))
        return result


class AuthCheck:
    """ Configurable function that allows to check for some kind of authentication """

    def __init__(self, auth_function: Callable[[TelegramEvent], bool], error_text: str):
        """
        :param Callable[[TelegramEvent], bool] auth_function:
            The function used to authenticate the user; It should return True if the user was authenticated, else False.
        :param str or None error_text:
            The Text the user will be shown if auth_function returns False.
            By default, it shows "Access denied".
        :return: None if the authorization was successful
        :raise: TelegramUserError if the authorization was not successful.
        """
        self.auth_function = auth_function
        self.error_text = error_text if error_text else "Access denied"

    def __call__(self, update: Update, context: CallbackContext):
        if self.auth_function(TelegramEvent(update, context)):
            return
        raise TelegramUserError(self.error_text)
