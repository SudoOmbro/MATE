import json

from telegram.ext import CommandHandler

from MateWrapper.bot import TelegramBot
from MateWrapper.globals import Globals
from MateWrapper.menus import Menu, Panel, FuncButton, InputButton
from MateWrapper.prompts import Prompt
from MateWrapper.handlers import TextHandler
from MateWrapper.variables import GetText


def main():
    with open("config.json", "r") as file:
        config_json = json.load(file)
    bot = TelegramBot(config_json["token"], name="test")
    bot.add_handler(Menu(
        entry_points=[CommandHandler("start", Globals.ENTRY_POINT)],
        panels={
            "main": Panel(
                "Hi there {__name}, what do you want to do?",
                [
                    [
                        FuncButton(
                            "show ID",
                            Prompt("Your id is `{__id}`")
                        ),
                        InputButton(
                            "Echo",
                            Prompt("okay, send some text", delete_last_message=True, keyboard=Globals.BACK_KEYBOARD),
                            TextHandler(GetText("text"))
                        )
                    ],
                    FuncButton(
                        "What did i say?",
                        Prompt("You said: '{text}'")
                    ),
                ],
                back_to=Globals.CLOSE_MENU,
            )
        },
        main_panel="main",
        fallbacks=[CommandHandler("end", Globals.END_HANDLER)]
    ))
    bot.add_handler(
        CommandHandler("about", Prompt(
            "Bot made by [SudoOmbro](https://github.com/SudoOmbro)",
            use_markdown=True)
        )
    )
    bot.start_and_idle()


if __name__ == '__main__':
    main()
