import json

from MateWrapper.bot import TelegramBot
from MateWrapper.handlers import TextHandler
from MateWrapper.prompts import Prompt


def main():
    with open("config.json", "r") as file:
        config_json = json.load(file)
    bot = TelegramBot(config_json["token"], name="test")
    bot.add_handler(TextHandler(Prompt("You are {__name} and said '{_text}'")))
    bot.start_and_idle()


if __name__ == '__main__':
    main()
