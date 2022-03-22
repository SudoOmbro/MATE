Context directives
==================

These little strings between curly brackets are quite useful in aiding the programmer in handling the user's context.
They can be used for both printing & storing stuff, a list of directives you can use for each type of function follows.

Of course the names we're using (except for {_text} & {_query})
are generic and can be replaced with any string.

Prompt
------

- **{var}**:
    This directive will retrieve whatever is stored in context.chat_data["var"]
    and replace the directive with it.
    If nothing is found then it will replace it with an empty string
- **{dict:var}**:
    This directive will retrieve whatever is stored in context.chat_data["dict"]["var"]
    and replace the directive with it.
    If nothing is found then it will replace it with an empty string
- **{obj:var}**:
    This directive will retrieve whatever is stored in context.chat_data["obj"].var
    and replace the directive with it.
    If nothing is found then it will replace it with an empty string
- **{__var}**:
    This directive will retrieve whatever is stored in update.effective_user["var"]
    and replace the directive with it.
    If nothing is found then it will replace it with an empty string.
    A couple valid directives are for example *{__id}* & *{__name}*
- **{_text}**:
    This directive will retrieve the text that the user
    just sent & replace the directive with it.
- **{_query}**:
    This directive will retrieve the data contained in the button just pressed by the user
    & replace the directive with it.

VarGetter
---------

- **{var}**:
    This directive will put the user's input in context.chat_data["var"].
- **{dict:var}**:
    This directive will put the user's input in context.chat_data["dict"]["var"].
    In case no dict is found in context.chat_data["dict"], a new dict is created.
- **{obj:var}**:
    This directive will put the user's input in context.chat_data["obj"].var.
    In case no object is found in context.chat_data["obj"], an exception is raised.
