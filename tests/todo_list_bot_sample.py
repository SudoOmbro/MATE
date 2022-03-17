import json
from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CommandHandler, CallbackContext

from MateWrapper.bot import TelegramBot
from MateWrapper.globals import Globals
from MateWrapper.menus import Menu, Panel, FuncButton, InputButton, CustomPanel
from MateWrapper.prompts import Prompt
from MateWrapper.handlers import TextHandler, ButtonHandler
from MateWrapper.variables import GetText, InitDefaultContext
from MateWrapper.generics import Chain, TelegramEvent


# Classes

class TODOEntry:

    LAST_ID: int = 0

    def __init__(self, title: str, text: str):
        self.id: int = TODOEntry.LAST_ID
        TODOEntry.LAST_ID += 1
        self.title = title
        self.text = text

    def __str__(self):
        return f"*{self.title}\n\n{self.text}*"


class EntryList:

    def __init__(self):
        self.entry_list: List[TODOEntry] = []

    def get_entry(self, entry_id: int):
        for entry in self.entry_list:
            if entry.id == entry_id:
                return entry
        return None

    def delete_entry(self, entry_id: int):
        entry = self.get_entry(entry_id)
        self.entry_list.remove(entry)

    def get_keyboard(self) -> InlineKeyboardMarkup:
        keyboard_list: List[List[InlineKeyboardButton]] = []
        for entry in self.entry_list:
            keyboard_list.append([
                InlineKeyboardButton(entry.title, callback_data=f"show {entry.id}"),
                InlineKeyboardButton("\U0000270F", callback_data=f"edit {entry.id}"),  # Pencil emoji
                InlineKeyboardButton("\U0001F5D1", callback_data=f"del {entry.id}")  # Trash emoji
            ])
        keyboard_list.append([InlineKeyboardButton("\U00002795", callback_data="add")])  # Plus emoji
        keyboard_list.append(Globals.BACK_BUTTON)
        return InlineKeyboardMarkup(keyboard_list)


# Custom callback handlers

def get_id_from_query(update: Update) -> int:
    return int(update.callback_query.data.split(" ")[1])


def show_todo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    entry_id = get_id_from_query(update)
    context.bot.send_message(text=context.chat_data["list"].get_entry(entry_id), chat_id=chat_id)


def delete_todo(update: Update, context: CallbackContext):
    pass


# Bot

def main():
    with open("config.json", "r") as file:
        config_json = json.load(file)
    bot = TelegramBot(config_json["token"], name="test")
    bot.add_handler(Menu(
        entry_points=[
            CommandHandler("start", Chain(
                InitDefaultContext({"list": EntryList()}),
                Globals.ENTRY_POINT
            ))
        ],
        panels={
            "main": CustomPanel(
                Prompt(
                    "Here are your TODOs",
                    keyboard=lambda event: event.context.chat_data["list"].get_keyboard(),
                    delete_last_message=True
                ),
                [
                    ButtonHandler(show_todo, pattern="show [0-9]+"),
                    ButtonHandler(Chain(), pattern="edit [0-9]+"),  # TODO add a GOTO instruction
                    ButtonHandler(Chain(), pattern="del [0-9]+"),
                    ButtonHandler(Chain(), pattern="add")
                ]
            ),
            "edit": Panel(
                "{current_todo}",
                buttons=[
                    InputButton(
                        "Edit title",
                        Prompt("Write the new title\n\n`{current_todo.title}`", use_markdown=True),
                        TextHandler(GetText("current_todo.title"))
                    ),
                    InputButton(
                        "Edit text",
                        Prompt("Write the new text\n\n`{current_todo.text}`", use_markdown=True),
                        TextHandler(GetText("current_todo.text"))
                    )
                ],
                back_to="main"
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
