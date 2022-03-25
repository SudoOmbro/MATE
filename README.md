# 🦙 MATE
_The Easy Telegram Application Maker_

Welcome to MATE, the open source wrapper for the 
[PythonTelegramBot wrapper](https://github.com/python-telegram-bot/python-telegram-bot)
that makes building telegram applications very **easy** and **intuitive** by adopting 
a **minimal** coding style!

## Design

MATE is designed as a way to build telegram applications which involves **using as little
custom code as possible**, relying on tested and safe solutions to do *~90%* of the work 
while injecting custom logic where necessary.

It's components are also easily extensible and reusable to allow for a wide degree of 
flexibility.

There are 5 main types of components:

- ### Prompts:
    A Prompt is what is used to send messages to users, they support Markdown formatting,
    web previews, keyboards and variable insertion without writing any additional 
    code other than the message itself!
- ### Getters
    A Getter is what is used to get any input from the User, it supports anything
    from text to keyboard inputs and even photos!
- ### Handlers
    A convenient way of abstracting away some complexity tied to the PythonTelegramBot
    wrapper and making the code more readable in the process!
- ### Chains
    These Chains aren't of the binding kind! Chains let you chain together multiple
    functions (handlers, getters, custom functions or even other chains) in order to
    build complex user interactions using the least possible amount of custom code!
- ### Menus
    Connect everything togheter in an easy way with Menus and the ready-made 
    Panels & Buttons that come with them!

## Docs

Read the documentation [here](https://matewrapper.readthedocs.io/en/latest/)!

## Contributing

IDK how this works yet but if there is any interest in the project i'll look into it :)