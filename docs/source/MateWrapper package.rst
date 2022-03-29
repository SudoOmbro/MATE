MateWrapper
===========
This package contains all the basic classes that wrap around the python telegram bot ext package
to ease bot development, like handlers, prompts & getters.

bot module
----------
This module contains the base bot wrapper and the defualt error handler.

.. automodule:: MateWrapper.bot
   :members:
   :special-members: __init__

generics module
---------------
This module contains stuff that is used all around the wrapper & Chains.

.. automodule:: MateWrapper.generics
   :members:
   :special-members: __init__

handlers module
---------------
This module contains convenient wrappers for handlers from the basic telegram wrapper.

.. automodule:: MateWrapper.handlers
   :members:
   :special-members: __init__

prompts module
--------------
This module contains all functions & classes related to prompts,
the easy way to handle complex responses.

.. automodule:: MateWrapper.prompts
   :members:
   :special-members: __init__

variables module
----------------
This module contains all functions & classes used by the wrapper to access the context.
Normally you are not going to touch this module but it's documented for posterity.

.. automodule:: MateWrapper.variables
   :members:
   :special-members: __init__

globals module
--------------
This module contains a bunch of constants & globals used all around the wrapper.

.. autoclass:: MateWrapper.globals.Globals
   :members:
