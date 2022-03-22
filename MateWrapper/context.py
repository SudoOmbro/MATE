from typing import Dict, Tuple

from MateWrapper.generics import TelegramEvent

[

    CONTEXT_VARIABLE,
    CONTEXT_DICT,
    CONTEXT_OBJECT,
    UPDATE_USER,
    UPDATE_TEXT,
    UPDATE_QUERY

] = range(6)


class MATEVarHandler:
    """
    Handles access to value either in the update or the context.

    This class is generic and nis implemented in MATEVarGetter & MATEVarSetter.

    These kind of classes aren't supposed to be instanced manually
    but are instead automatically instanced by the wrapper.
    """

    HANDLERS: Dict[int, Tuple[callable, callable or None]]

    # handlers structure:
    # type - handler, lambda to get the args or None

    def __init__(self, target: str):
        """
        :param target:
            the target variable to set/get. Special characters can change it's behaviour:
            - target = "name":
                simply set/retrieve the value of context.chat_data["name"]
            - target = "dictionary:value"
                set/retrieve the value of context.chat_data["dictionary"]["value"],
                where context.chat_data["dictionary"] is a dictionary
            - target = "object.variable":
                set/retrieve the value of context.chat_data["object"].variable,
                where context.chat_data["object"] is an object
            - target = "_parameter":
                retrieve the value "parameter" from update.effective_user (like "id" or "name")
        """
        var_type = self.__get_access_type(target)
        # Get the correct handler from the inferred variable type. If there is no handler throw an Exception
        handlers: Tuple[callable, callable] = self.HANDLERS.get(var_type, None)
        if not handlers:
            raise ValueError(f"No handler for var_type {var_type} (target: {target})")
        # Set logic and get args through the given lambda
        self.logic: callable = handlers[0]
        if handlers[1]:
            self.args = handlers[1](target)
        else:
            self.args = target

    @staticmethod
    def __get_access_type(target: str):
        if target.find(":") != -1:
            return CONTEXT_DICT
        elif target.find(".") != -1:
            return CONTEXT_OBJECT
        elif target[:2] == "__":
            return UPDATE_USER
        elif target == "_text":
            return UPDATE_TEXT
        elif target == "_query":
            return UPDATE_QUERY
        else:
            return CONTEXT_VARIABLE

    def __str__(self):
        return str(self.__dict__)


class MATEVarGetter(MATEVarHandler):
    """
    Handles getting variables from the context, can access update data
    """

    def __get_variable(self, event: TelegramEvent):
        return event.context.chat_data[self.args]

    def __get_dict(self, event: TelegramEvent):
        return event.context.chat_data[self.args[0]][self.args[1]]

    def __get_object(self, event: TelegramEvent):
        return event.context.chat_data[self.args[0]].__dict__[self.args[1]]

    def __get_from_update_user(self, event: TelegramEvent):
        return event.update.effective_user[self.args]

    def __get_update_text(self, event: TelegramEvent):
        return event.update.message.text

    def __get_update_query(self, event: TelegramEvent):
        return event.update.callback_query.data

    HANDLERS = {
        CONTEXT_VARIABLE: (
            __get_variable,
            None
        ),
        CONTEXT_DICT: (
            __get_dict,
            lambda target: target.split(":")
        ),
        CONTEXT_OBJECT: (
            __get_object,
            lambda target: target.split(".")
        ),
        UPDATE_USER: (
            __get_from_update_user,
            lambda target: target[2:]
        ),
        UPDATE_TEXT: (
            __get_update_text,
            None
        ),
        UPDATE_QUERY: (
            __get_update_query,
            None
        )
    }


class MATEVarSetter(MATEVarHandler):
    """
    Handles setting variables in the context, cannot access update data
    """

    def __set_variable(self, user_input, event: TelegramEvent):
        event.context.chat_data[self.args] = user_input

    def __set_object(self, user_input, event: TelegramEvent):
        event.context.chat_data[self.args[0]].__dict__[self.args[1]] = user_input

    def __set_dict(self, user_input, event: TelegramEvent):
        if event.context.chat_data[self.args[0]] is None:
            event.context.chat_data[self.args[0]] = {}
        event.context.chat_data[self.args[0]][self.args[1]] = user_input

    HANDLERS = {
        CONTEXT_VARIABLE: (
            __set_variable,
            None
        ),
        CONTEXT_DICT: (
            __set_dict,
            lambda target: target.split(":")
        ),
        CONTEXT_OBJECT: (
            __set_object,
            lambda target: target.split(".")
        )
    }
