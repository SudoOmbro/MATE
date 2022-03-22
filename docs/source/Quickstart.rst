Quickstart
==========
A collection of small guides to get you going fast with the wrapper,
aimed to teach the basics and how to best use the features of this wrapper.

Your first bot
--------------
Let's build a simple echo bot as a first example:

First of all, let's be good programmers and let's setup our main :)

.. code-block:: python

    def main():
        pass


    if __name__ == "__main__":
        main()

To use the bot, you'll need an Access Token. To generate an Access Token,
you have to talk to **@BotFather** and follow a few simple steps
(described `here <https://core.telegram.org/bots#6-botfather>`_).

Now that you have a telegram bot token, let's import what we'll need:
- The bot itself of course
- A TextHandler, basically an object that handles text messages from the user
- A Prompt, basically a 'configurable function' that allow the programmer to send a message.

.. code-block:: python

    from MateWrapper.bot import TelegramBot
    from MateWrapper.handlers import TextHandler
    from MateWrapper.prompts import Prompt


    def main():
        pass


    if __name__ == "__main__":
        main()

There, now that we have what we need, let's put everything together.
To instance a bot, just create a TelegamBot object:

.. code-block:: python

    bot = TelegramBot(token="your bot token", name="your bot name (this is entirely optional)")

then, to add an handler to our newly created bot we just need to call our bots *add_handler* method and pass in
a text handler that itself will call a prompt:

.. code-block:: python

    bot.add_handler(TextHandler(Prompt("you said: {_text}")))

With this instruction we are basically telling the bot that, when it receives a text message,
it should send a text message containing *"you said: {_text}"*.


Speaking of prompts, whenever you put a word between curly brackets in the text, you are giving the prompt a
**context directive**, these can be of many different types, in our case we are using a special type of
directive exclusive to prompts that will be replace with the text that the user just sent.

For more info about **context directives**, see :doc:`Context directives`.

Back to our echo bot, it's finished! Now all we have to do is start it, which you can with the following instruction:

.. code-block:: python

    bot.start_and_idle()

And there you go! We are done! Here's how your entire bot should look like:

.. code-block:: python

    from MateWrapper.bot import TelegramBot
    from MateWrapper.handlers import TextHandler
    from MateWrapper.prompts import Prompt


    def main():
        bot = TelegramBot(token="your bot token", name="your bot name (this is entirely optional)")
        bot.add_handler(TextHandler(Prompt("you said: {_text}")))
        bot.start_and_idle()


    if __name__ == "__main__":
        main()

That wasn't so bad, was it?

Now when you start the bot (assuming the token you used is valid) and write for exaple "hi" to it,
it should respond with "you said: hi".

3 lines of code for an echo bot is pretty good, but keep reading, it gets better ;)

Using Menus
-----------
Now, while Prompts are quite convenient & Building bots that echo what you said or tell you your name/id is pretty cool,
where this wrapper gets spicy is with the introduction Menus, Panels & Buttons

TODO

Advanced usage
--------------
TODO