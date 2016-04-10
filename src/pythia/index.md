AST Translation
---------------

Abstract Syntax Trees (AST) translate source code into objects you can traverse over
and generate new code in the process.  The `ast` module is built into Python, and is
the standard way to translate python source code into another language. 

The best documentation on the Python `ast` module is [Green Tree Snakes](https://greentreesnakes.readthedocs.org/en/latest/)

Pythia Source Code
------------------
Most of Pythia's source code is written in markdown files, and compiled by `pythia.py` which loads `main.md`
