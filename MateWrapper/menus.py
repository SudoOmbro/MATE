from typing import Dict, List

from telegram.ext import Handler, CallbackQueryHandler

from MateWrapper.generics import TelegramFunctionBlueprint
from MateWrapper.prompts import Prompt
from MateWrapper.generics import Chain


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
