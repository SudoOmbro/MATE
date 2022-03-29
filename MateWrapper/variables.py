from copy import deepcopy
from re import match
from typing import Callable, Union

from telegram import Update
from telegram.ext import CallbackContext

from MateWrapper.context import MATEVarSetter
from MateWrapper.generics import TelegramFunctionBlueprint, TelegramEvent, TelegramUserError


class GetVariableGeneric(TelegramFunctionBlueprint):
    """ Generic class to handle getting variables in the wrapper, needs to be implemented """

    def __init__(
            self,
            var_name: str or None,
            transformation_function: Union[Callable[[object, TelegramEvent], object], None] = None,
            next_state: int or None = None,
            custom_setter_function: Union[Callable[[object, str], object], None] = None
    ):
        """
        :param str or None var_name:
            name of the variable to store, this will be put in context.chat_data

            if you pass None (and return value is None), this handler will just return the retrieved value. Useful in
            combination with transformation functions to use the gathered data in some way and then throw it away or
            to create main menus that lead to submenus.

            if you pass something like "dict_name:aaa" then this handler will try to put the received value in
            dict_name["aaa"], where dict_name is the context key for the dict and aaa is a parameter of said dict

            if you pass something like "obj_name.var" then this handler will try to put the received value in
            obj_name.var, where onj_name is the context key for the object and var is a variable of said object
        :param Union[Callable[[object, TelegramEvent], object], None] transformation_function:
            a function that will take the variable and transform it somehow before storing it.

            the function should have 2 inputs and 1 output, like this:

            func(input, event: TelegramEvent):
                return something
        :param int or None next_state:
            the return value of the function, used to change state in conversation handlers.
            Leave at None to not change state.
        :param Union[Callable[[object, str], object], None] custom_setter_function:
            a custom setter function useful for interacting with objects outside of the context.

            the function should have 2 inputs and optionally an integer output, like this:

            func(input, var_name: str)
                ...

                next_state: int = 1

                return next_state
        """
        # set transformation
        if transformation_function:
            self.transformation_func = transformation_function
            self.__get: callable = self.__get_from_source_transform
        else:
            self.__get: callable = self.__get_from_source_no_transform
        # set where to put the value
        if var_name:
            if custom_setter_function:
                self.logic: callable = self.__custom_setter_handler
                self.custom_setter_function: callable = custom_setter_function
                self.var_name: str = var_name
            else:
                self.logic: callable = self.__set
                self.set_handler: MATEVarSetter = MATEVarSetter(var_name)
        else:
            self.logic = self.__no_set
        self.next_state = next_state

    # get handling

    def __get_from_source_transform(self, event: TelegramEvent):
        return self.transformation_func(self.get_from_source(event), event)

    def __get_from_source_no_transform(self, event: TelegramEvent):
        return self.get_from_source(event)

    # set handling

    def __set(self, event: TelegramEvent):
        self.set_handler.logic(self.set_handler, self.__get(event), event)
        return self.next_state

    def __custom_setter_handler(self, event: TelegramEvent):
        return_value = self.custom_setter_function(self.__get(event), self.var_name)
        if return_value:
            return return_value
        return self.next_state

    def __no_set(self, event: TelegramEvent):
        if self.next_state:
            self.__get(event)
            return self.next_state
        return self.__get(event)

    # Abstract function that needs to be implemented

    def get_from_source(self, event: TelegramEvent):
        raise NotImplemented


class GetText(GetVariableGeneric):
    """ Gets a text input from the user and optionally validates it, use in conjunction with TextHandler """

    def __init__(
            self,
            var_name: str or None,
            transformation_function: callable or None = None,
            validation_regex: str = None,
            error_message: str = None,
            next_state: object or None = None,
            custom_setter_function: callable or None = None
    ):
        """
        :param str validation_regex:
            The regular expression used to validate the text input.
            Leave empty if you don't want to validate
        :param str error_message:
            The error message to send the user in case the given input wasn't validated correctly.
            Leave empty for a default, generic response
        :raise TelegramUserError:
            if validation is enabled and the given text doesn't match
            the given regex this function will raise a TelegramUserError with the given error_message as error message.
        """
        super().__init__(
            var_name,
            transformation_function=transformation_function,
            next_state=next_state,
            custom_setter_function=custom_setter_function
        )
        if validation_regex:
            self.validation_regex = validation_regex
            self.get_from_source: callable = self.get_validation
        else:
            self.get_from_source: callable = self.get_no_validation
        self.error_message = error_message if error_message else "The given text doesn't match the pattern"

    def get_validation(self, event: TelegramEvent):
        text = event.update.message.text
        if match(self.validation_regex, text):
            return event.update.message.text
        raise TelegramUserError(self.error_message)

    @staticmethod
    def get_no_validation(event: TelegramEvent):
        return event.update.message.text


class GetKeyboardInput(GetVariableGeneric):
    """ Gets an input from a keyboard, use in conjunction with ButtonHandler """

    # TODO? add support for arbitrary_callback_data
    # (I have never used this but the base library supports it so maybe?)

    def get_from_source(self, event: TelegramEvent):
        return event.update.callback_query.data


class GetPhoto(GetVariableGeneric):
    """ Gets a photo from a PhotoMessage, use in conjunction with PhotoHandler """

    def get_from_source(self, event: TelegramEvent):
        file = event.update.message.photo[-1].get_file()
        return bytes(file.download_as_bytearray())


def clear_vars(update: Update, context: CallbackContext):
    """ Used to clear the current user context """
    context.chat_data.clear()


class InitDefaultContext(TelegramFunctionBlueprint):
    """ Used to set the given dictionary as the current user's context. """

    def __init__(self, default_context: dict, clear_context: bool = False):
        """
        :param dict default_context: the desired context
        :param bool clear_context: defines whether the user's context should be cleared before initializing the new one
        """
        self.default_context = default_context
        self.clear_context = clear_context

    def logic(self, event: TelegramEvent):
        if self.clear_context:
            clear_vars(event.update, event.context)
        for item in self.default_context:
            event.context.chat_data[item] = deepcopy(self.default_context[item])
