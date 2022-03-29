from typing import Callable, Union, List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import Handler, CallbackContext

from MateMenus.generics import GenericPanel, Button, MenuContext, get_back_button_handler
from MateWrapper.generics import TelegramEvent, Chain
from MateWrapper.globals import Globals
from MateWrapper.prompts import Prompt


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
    def _add_button_handler(context: MenuContext, current_handlers: List[Handler], button: Button):
        button.compile(context)
        handler = button.get_handler()
        if handler:
            current_handlers.append(handler)
        next_state_handler = button.get_next_state_handlers()
        if next_state_handler:
            context.current_menu.states[button.handle] = next_state_handler

    def get_handlers(self, context: MenuContext) -> List[Handler]:
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

    def compile(self, context: MenuContext):
        if self.destination_panel not in context.panels:
            raise ValueError(f"The specified panel '{self.destination_panel}' is not defined")
        self.prompt = context.panels[self.destination_panel].prompt


class CustomPanel(GenericPanel):
    """ An extremely simple implementation of a Panel, useful for building very dynamic apps """

    def __init__(self, prompt: Prompt, handlers: List[Handler], auto_handle_state: bool = True):
        """
        :param prompt: The prompt that will be shown by this panel
        :param handlers: The list of handlers tied to this panel
        :param auto_handle_state: Define if the prompt's state will be automatically handled by the wrapper.
        """
        self.prompt = prompt
        self.handlers = handlers
        self.auto_handle_state = auto_handle_state

    def set_prompt(self, current_state: object):
        if self.auto_handle_state:
            self.prompt.next_state = current_state

    def get_handlers(self, context: MenuContext) -> List[Handler]:
        for handler in self.handlers:
            if type(handler.callback) == Chain:
                for func in handler.callback.functions:
                    if hasattr(func, "compile"):
                        func.compile(context)
            elif hasattr(handler.callback, "compile"):
                handler.callback.compile(context)
        return self.handlers
