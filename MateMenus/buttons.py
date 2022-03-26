from typing import List

from telegram import InlineKeyboardButton
from telegram.ext import Handler, CallbackQueryHandler

from MateMenus.generics import Button, MenuContext, GenericPanel, get_back_button_handler
from MateWrapper.generics import Chain
from MateWrapper.prompts import Prompt


class GotoButton(Button):
    """ button that allows for Panel changing """

    handler: Handler

    def __init__(self, text: str, next_panel: str):
        super().__init__(text)
        self.next_panel = next_panel

    def compile(self, context: MenuContext):
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

    current_panel: "GenericPanel"

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

    def compile(self, context: MenuContext):
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
