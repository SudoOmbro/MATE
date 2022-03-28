from typing import Callable, List

from telegram import Update
from telegram.ext import Handler, CallbackContext

from MateMenus.generics import GenericPanel, MenuContext, AuthCheck
from MateWrapper.generics import TelegramEvent, Chain
from MateWrapper.prompts import Prompt


class Decorated(GenericPanel):
    """
    A Wrapper of GenericPanel that adds ``function`` to the start/end of every function in wrapped_panel.
    """

    def __init__(
            self,
            wrapped_panel: GenericPanel,
            function: Callable[[Update, CallbackContext], object],
            mode: int = 0
    ):
        """
        :param GenericPanel wrapped_panel:
            the panel wrapped by this class.
        :param Callable[[TelegramEvent], object] function:
            The function that will be executed first/last by every handler in wrapped_panel.
        :param int mode:
            if 0, function will be added before every other function.
            if 1, function will be added after every other function.
            By default, it's 0.
        """
        self.wrapped_panel = wrapped_panel
        self.function = function
        if mode not in (0, 1):
            raise ValueError("The mode can only be 0 or 1")
        self.mode = mode

    def set_prompt(self, current_state: object):
        self.wrapped_panel.set_prompt(current_state)

    def get_handlers(self, context: MenuContext) -> List[Handler]:
        handlers = self.wrapped_panel.get_handlers(context)
        for handler in handlers:
            if self.mode == 0:
                handler.callback = Chain(self.function, handler.callback)
            else:
                handler.callback = Chain(handler.callback, self.function)
        return handlers


class Private(Decorated):
    """
    A ready-made wrapper of GenericPanel useful for building "private"
    Panels that require some kind of authentication to access.
    """

    def __init__(
        self,
        wrapped_panel: GenericPanel,
        auth_function: Callable[[TelegramEvent], bool],
        error_text: Prompt or None = None
    ):
        """
        :param GenericPanel wrapped_panel:
            the panel wrapped by this class.
        :param Callable[[TelegramEvent], bool] auth_function:
            see ``AuthCheck``.
        :param str or None error_text:
            see ``AuthCheck``.
        """
        super().__init__(wrapped_panel, AuthCheck(auth_function, error_text))
