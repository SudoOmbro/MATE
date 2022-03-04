import json

from telegram.ext import CommandHandler

from MateWrapper.bot import TelegramBot
from MateWrapper.handlers import Conversation, END_CONVERSATION
from MateWrapper.prompts import Prompt
from MateWrapper.utils import generate_keyboard, MenuHandler, Chain

MAIN_MENU_PROMPT = Prompt(
    "Hi! What do you want me to do?",
    generate_keyboard([
            [
                {
                    "text": "say hi to me!",
                    "data": "hi"
                },
                {
                    "text": "tell me my id!",
                    "data": "id"
                }
            ]
        ],
        add_back_button=True
    ),
    return_value=0,
    delete_last_message=True
)
END_PROMPT = Prompt(
    "Conversation finished",
    return_value=END_CONVERSATION,
    delete_last_message=True
)


def main():
    with open("config.json", "r") as file:
        config_json = json.load(file)
    bot = TelegramBot(config_json["token"], name="test")
    bot.add_handler(Conversation(
        entry_points=[CommandHandler("start", MAIN_MENU_PROMPT)],
        states={
            0: MenuHandler(
                {
                    "hi": Chain(
                        Prompt("hi {__name}! Nice to meet you!"),
                        MAIN_MENU_PROMPT
                    ),
                    "id": Chain(
                        Prompt("Your id is {__id}"),
                        MAIN_MENU_PROMPT
                    )
                },
                previous_menu=END_PROMPT
            )
        },
        fallbacks=[CommandHandler("end", END_PROMPT)]
    ))
    bot.add_handler(CommandHandler("about", Prompt("This bot was made by @LordOmbro")))
    bot.start_and_idle()


if __name__ == '__main__':
    main()
