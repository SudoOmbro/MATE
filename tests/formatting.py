from MateWrapper.context import MATEVarGetter, MATEVarSetter


# Mockup classes

class TestObj:

    def __init__(self):
        self.var = "Age of Pixels"


class Update:

    def __init__(self):
        self.effective_user: dict = {
            "id": 123456789,
            "name": "Ombro"
        }


class CallbackContext:

    def __init__(self):
        self.chat_data: dict = {
            "var": "Boomzerk",
            "obj": TestObj(),
            "dict": {
                "var": "SAM"
            }
        }


class TelegramEvent:

    def __init__(self):
        self.update = Update()
        self.context = CallbackContext()


# tests

def getter_autoconfig_test():
    simple_getter = MATEVarGetter("var")
    object_getter = MATEVarGetter("obj.var")
    dict_getter = MATEVarGetter("dict:var")
    update_user_getter = MATEVarGetter("__var")
    update_data_getter = MATEVarGetter("_var")
    print(simple_getter)
    assert simple_getter.args == "var"
    print(object_getter)
    assert object_getter.args == ["obj", "var"]
    print(dict_getter)
    assert dict_getter.args == ["dict", "var"]
    print(update_user_getter)
    assert update_user_getter.args == "var"
    print(update_data_getter)
    assert update_data_getter.args == "var"
    print("getter_autoconfig_test passed")


def setter_autoconfig_test():
    simple_setter = MATEVarSetter("var")
    object_setter = MATEVarSetter("obj.var")
    dict_setter = MATEVarSetter("dict:var")
    print(simple_setter)
    assert simple_setter.args == "var"
    print(object_setter)
    assert object_setter.args == ["obj", "var"]
    print(dict_setter)
    assert dict_setter.args == ["dict", "var"]
    print("setter_autoconfig_test passed")


if __name__ == '__main__':
    getter_autoconfig_test()
    setter_autoconfig_test()
