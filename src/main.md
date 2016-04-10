Pythia Source Code
-------------------

You need to be familiar with the Python AST module to understand how Pythia works.
The best guide to Python AST is here: [Green Tree Snakes](https://greentreesnakes.readthedocs.org/en/latest/)

Script Header
-------------
```python
import os, sys
import ast, itertools, json

```

First Stage Translator
----------------------
* [@import helper function](pythia/genmarkdown.md) converts folders and files into pythia markdown containers.
* [@import pythia syntax pre-processor](pythia/typedpython.md) converts source into python AST compatible code.
* [@import helper functions for AST processing](pythia/astutils.md) used mostly by the first stage of translation.
* [@import helper codewriter class](pythia/codewriter.md)
* [@import first stage of translator](pythia/intermediateform.md)

Second Stage Translator
-----------------------
* [@import multi-backend base class](pythia/generatorbase.md)
* [@import javascript translator](pythia/jstranslator.md)
* [@import golang translator](pythia/gotranslator.md)
* [@import rust and c++](pythia/cpprustbase.md) shared base class logic.
* [@import rust translator](pythia/rusttranslator.md)
* [@import c++14 translator](pythia/cpptranslator.md)

