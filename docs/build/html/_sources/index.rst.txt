.. MATE documentation master file, created by
   sphinx-quickstart on Sat Mar 19 15:08:45 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to MATE's documentation!
================================

The *Easy Telegram Application Maker*

.. code-block::

   pip install mate-wrapper

What is MATE?
-------------
MATE is a way of building telegram applications which involves **using as little
custom code as possible**, relying on tested and safe solutions to do *~90%* of the work
while injecting custom logic only where necessary.

It has 2 main packages:

- :doc:`MateWrapper package`:
   The basic wrapper built around the python-telegram-bot telegram.ext package, provides functions & classes
   useful to simplify building bots while still using the base framework.
- :doc:`MateMenus package`:
   This package is built on top of the previous one and basically transforms MATE into it's own framework.


Index
-----

.. toctree::

   Quickstart
   MateWrapper package
   MateMenus package
   Context directives
