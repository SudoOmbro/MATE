import json
from typing import List

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, ParseMode
from telegram.ext import CommandHandler, CallbackContext

from MateWrapper.bot import TelegramBot
from MateWrapper.globals import Globals
from MateMenus.keyboards import get_keyboard_from_list_custom_row
from MateWrapper.prompts import Prompt
from MateWrapper.handlers import TextHandler, ButtonHandler
from MateWrapper.variables import GetText, InitDefaultContext
from MateWrapper.generics import Chain, TelegramEvent

from MateMenus.buttons import InputButton
from MateMenus.generics import Menu
from MateMenus.panels import CustomPanel, GOTO, Panel


# Model

class TODOEntry:

    LAST_ID: int = 0

    def __init__(self, title: str, text: str):
        self.id: int = TODOEntry.LAST_ID
        TODOEntry.LAST_ID += 1
        self.title = title
        self.text = text

    def __str__(self):
        return f"*{self.title}*\n\n_{self.text}_"


class EntryList:

    def __init__(self):
        self.entry_list: List[TODOEntry] = []

    def get_entry(self, entry_id: int) -> TODOEntry or None:
        for entry in self.entry_list:
            if entry.id == entry_id:
                return entry
        return None

    def delete_entry(self, entry_id: int):
        entry = self.get_entry(entry_id)
        self.entry_list.remove(entry)

    def add_entry(self) -> TODOEntry:
        new_entry = TODOEntry("new entry", "text")
        self.entry_list.append(new_entry)
        return new_entry


# Controller

def get_id_from_query(update: Update) -> int:
    return int(update.callback_query.data.split(" ")[1])


def get_todo_keyboard_row(entry: TODOEntry) -> List[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(entry.title, callback_data=f"show {entry.id}"),
        InlineKeyboardButton("\U0000270F", callback_data=f"edit {entry.id}"),  # Pencil emoji
        InlineKeyboardButton("\U0001F5D1", callback_data=f"del {entry.id}")  # Trash emoji
    ]


TODO_KEYBOARD_ADD = [[InlineKeyboardButton("\U00002795", callback_data="add")]]  # Plus emoji


def get_todo_keyboard(event: TelegramEvent) -> InlineKeyboardMarkup:
    return get_keyboard_from_list_custom_row(
        event.context.chat_data["list"].entry_list,
        get_todo_keyboard_row,
        post_keyboard=TODO_KEYBOARD_ADD,
        add_back_button=True
    )


def show_todo(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    entry_id = get_id_from_query(update)
    context.bot.send_message(
        text=str(context.chat_data["list"].get_entry(entry_id)),
        chat_id=chat_id,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def edit_todo(update: Update, context: CallbackContext):
    context.chat_data["current_todo"] = context.chat_data["list"].get_entry(get_id_from_query(update))


def delete_todo(update: Update, context: CallbackContext):
    context.chat_data["list"].delete_entry(get_id_from_query(update))


def add_todo(update: Update, context: CallbackContext):
    context.chat_data["current_todo"] = context.chat_data["list"].add_entry()


# Bot (view)

def main():
    """ Very simple app, does not save the context but that wouldn't be too hard to do """
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
                    keyboard=get_todo_keyboard,
                    delete_last_message=True
                ),
                [
                    ButtonHandler(show_todo, pattern="show [0-9]+"),
                    ButtonHandler(Chain(edit_todo, GOTO("edit")), pattern="edit [0-9]+"),
                    ButtonHandler(Chain(delete_todo, GOTO("main")), pattern="del [0-9]+"),
                    ButtonHandler(Chain(add_todo, GOTO("edit")), pattern="add"),
                    Globals.END_HANDLER
                ]
            ),
            "edit": Panel(
                "{current_todo}",
                buttons=[[
                    InputButton(
                        "Edit title",
                        Prompt("Write the new title\n\n`{current_todo.title}`", use_markdown=True, delete_last_message=True),
                        TextHandler(GetText("current_todo.title"))
                    ),
                    InputButton(
                        "Edit text",
                        Prompt("Write the new text\n\n`{current_todo.text}`", use_markdown=True, delete_last_message=True),
                        TextHandler(GetText("current_todo.text"))
                    )
                ]],
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
