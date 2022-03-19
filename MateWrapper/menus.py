from functools import cache
from typing import Dict, List, Union, Callable

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Handler, CallbackQueryHandler, ConversationHandler, CallbackContext

from MateWrapper.globals import Globals
from MateWrapper.prompts import Prompt
from MateWrapper.generics import Chain, TelegramEvent

__BUTTON_COUNTER: int = 0


def _get_button_handle() -> str:
    global __BUTTON_COUNTER
    current_id = __BUTTON_COUNTER
    __BUTTON_COUNTER += 1
    return f"__b{current_id}__"


class _MenuContext:
    """ Private class used by Menus to compile buttons and panels """

    def __init__(self, current_menu: "Menu", current_panel: "GenericPanel", panels: Dict[object, "GenericPanel"]):
        self.current_menu = current_menu
        self.current_panel = current_panel
        self.panels = panels


@cache
def get_back_button_handler(current_panel: "Panel") -> CallbackQueryHandler:
    return CallbackQueryHandler(current_panel.prompt, pattern=Globals.BACK_PATTERN)


class Button:
    """ generic keyboard button class to implement """

    def __init__(self, text: str):
        if not text:
            raise ValueError("A button needs some text in it")
        self.text: str = text
        self.handle: str = _get_button_handle()

    def compile(self, context: _MenuContext):
        pass

    def get_next_state_handlers(self) -> Handler or List[Handler] or None:
        return None

    def get_handler(self) -> Handler or None:
        return None

    def get_keyboard_button(self) -> InlineKeyboardButton:
        """ by default generates the button with its handle as callback data """
        return InlineKeyboardButton(self.text, callback_data=self.handle)


class GotoButton(Button):
    """ button that allows for Panel changing """

    handler: Handler

    def __init__(self, text: str, next_panel: str):
        super().__init__(text)
        self.next_panel = next_panel

    def compile(self, context: _MenuContext):
        if self.next_panel not in context.panels:
            raise ValueError(f"panel '{self.next_panel}' is not defined")
        self.handler = CallbackQueryHandler(context.panels[self.next_panel].prompt, pattern=self.handle)

    def get_handler(self) -> Handler or None:
        return self.handler


class UrlButton(Button):
    """ button that redirects the user to the specified url when clicked """

    def __init__(self, text: str, url: str):
        super().__init__(text)
        if not url:
            raise ValueError("The url cannot be empty")
        self.url = url

    def get_keyboard_button(self) -> InlineKeyboardButton:
        return InlineKeyboardButton(self.text, url=self.url)


class FuncButton(Button):
    """ button that executes a function (or a chain of functions) when clicked """

    def __init__(self, text: str, function: callable):
        super().__init__(text)
        if not function:
            raise ValueError("The function cannot be None")
        self.func = function

    def get_handler(self) -> Handler or None:
        return CallbackQueryHandler(self.func, pattern=self.handle)


class InputButton(Button):
    """
    button that makes getting inputs from users a lot easier by automating callback and state handling.
    """

    current_panel: "Panel"

    def __init__(self, text: str, prompt: Prompt, input_handlers: Handler or List[Handler]):
        """
        :param text (str):
            The text that will be shown in the button
        :param prompt (Prompt):
            The prompt that will be shown when acquiring the input from the user
        :param input_handle (Handler or List[Handler]):
            The function(s) that will be used to handle the user's input
        """
        super().__init__(text)
        self.prompt: Prompt = prompt
        if not input_handlers:
            raise ValueError("You must pass at least one input handler")
        self.nsh = input_handlers

    def compile(self, context: _MenuContext):
        self.current_panel = context.current_panel
        if type(self.nsh) == list:
            for handler in self.nsh:
                handler.callback = Chain(handler.callback, context.current_panel.prompt)
        else:
            self.nsh.callback = Chain(self.nsh.callback, context.current_panel.prompt)

    def get_next_state_handlers(self) -> List[Handler] or None:
        if type(self.nsh) != list:
            return [
                self.nsh,
                get_back_button_handler(self.current_panel)
            ]
        self.nsh.append(get_back_button_handler(self.current_panel))
        return self.nsh

    def get_handler(self) -> Handler or None:
        return CallbackQueryHandler(Chain(self.prompt, next_state=self.handle), pattern=self.handle)


class GenericPanel:
    """ Panel prototype """

    prompt: Prompt

    def set_prompt(self, current_state: object):
        raise NotImplemented

    def get_handlers(self, context: _MenuContext) -> List[Handler]:
        raise NotImplemented


class Panel(GenericPanel):
    """
    A complex implementation of a Panel that automatically handles callbacks & states
    """

    def __init__(
            self,
            prompt_text: Union[str, Callable[[TelegramEvent], str]],
            buttons: List[Union[Button, List[Button]]],
            back_to: str,
            extra_handlers: List[Handler] or None = None,
    ):
        """
        :param Union[str, Callable[[TelegramEvent], str]] prompt_text:
            The text that will be sent when this panel is shown,
            supports all the same formatting options as the Panel object.
            Can be callable.
        :param List[Union[Button, List[Button]]] buttons:
            The list of Button objects (or of List[Button]) that will define the functionality of this panel.
        :param str back_to:
            The name of the Panel to go back to. If "__end__" the back button will close the menu.
        :param List[Handler] or None extra_handlers:
            A list of extra handlers that can do extra stuff, like read text inputs and stuff like that.
        """
        self.buttons = buttons
        self.prompt_text = prompt_text
        self.back_to = back_to
        self.extra_handlers = extra_handlers

    def _get_keyboard(self) -> InlineKeyboardMarkup:
        """ generates a keyboard object from the list of buttons """
        keyboard_list: List[List[InlineKeyboardButton]] = []
        for button in self.buttons:
            if type(button) == list:
                keyboard_list.append([b.get_keyboard_button() for b in button])
            else:
                keyboard_list.append([button.get_keyboard_button()])
        keyboard_list.append([Globals.BACK_BUTTON])
        return InlineKeyboardMarkup(keyboard_list)

    def set_prompt(self, current_state: object):
        """ Generates the Prompt, call this before compiling handlers """
        self.prompt = Prompt(
            self.prompt_text,
            self._get_keyboard(),
            next_state=current_state,
            delete_last_message=True,
            use_markdown=True
        )

    @staticmethod
    def _add_button_handler(context: _MenuContext, current_handlers: List[Handler], button: Button):
        button.compile(context)
        handler = button.get_handler()
        if handler:
            current_handlers.append(handler)
        next_state_handler = button.get_next_state_handlers()
        if next_state_handler:
            context.current_menu.states[button.handle] = next_state_handler

    def get_handlers(self, context: _MenuContext) -> List[Handler]:
        """ returns a dictionary used to extend the main menu dictionary """
        result: List[Handler] = []
        # compile all button handlers and add them
        for element in self.buttons:
            if type(element) == list:
                for button in element:
                    self._add_button_handler(context, result, button)
            else:
                self._add_button_handler(context, result, element)
        # add back button if back_to is defined
        if self.back_to:
            if self.back_to == Globals.CLOSE_MENU:
                result.append(Globals.END_HANDLER)
            else:
                result.append(get_back_button_handler(context.panels[self.back_to]))
        # add the extra handlers if there are any
        if self.extra_handlers:
            result.extend(self.extra_handlers)
        return result


class GOTO:
    """ Compiles to the prompt of the panel given as destination_panel, useful for Changing Panel in a custom Panel """

    prompt: Prompt

    def __call__(self, update: Update, context: CallbackContext):
        return self.prompt(update, context)

    def __init__(self, destination_panel: str):
        self.destination_panel = destination_panel

    def compile(self, context: _MenuContext):
        if self.destination_panel not in context.panels:
            raise ValueError(f"The specified panel '{self.destination_panel}' is not defined")
        self.prompt = context.panels[self.destination_panel].prompt


class CustomPanel(GenericPanel):
    """ An extremely simple implementation of a Panel, useful for building very dynamic apps """

    def __init__(self, prompt: Prompt, handlers: List[Handler], auto_handle_state: bool = True):
        self.prompt = prompt
        self.handlers = handlers
        self.auto_handle_state = auto_handle_state

    def set_prompt(self, current_state: object):
        if self.auto_handle_state:
            self.prompt.next_state = current_state

    def get_handlers(self, context: _MenuContext) -> List[Handler]:
        for handler in self.handlers:
            if type(handler.callback) == Chain:
                for func in handler.callback.functions:
                    if hasattr(func, "compile"):
                        func.compile(context)
            elif hasattr(handler.callback, "compile"):
                handler.callback.compile(context)
        return self.handlers


class Menu(ConversationHandler):
    """
    A menu, container for one or more (usually more) panels
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
            self.states[panel_name] = panels[panel_name].get_handlers(_MenuContext(self, panels[panel_name], panels))
        return result
