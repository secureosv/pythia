Markdown Containers
-------------------

The primary format `pythia` works with is [markdown](https://guides.github.com/features/mastering-markdown/) containers files (`.md`).
Markdown containers allow you to bundle code and data into a single file.  They store project and file directory stucture,
code build options, and code documentation.

Markdown files that contain fenced-code-blocks using [github style markdown](https://help.github.com/categories/writing-on-github/), can be compiled and run with `pythia`.
Tripple backquotes `ʽʽʽ` are used to fence a block of code.  The start of a fence can contain a language name, like: `ʽʽʽc++`,
this will trigger that fenced code block to be compiled with `g++`.

Fenced code blocks can also contain a label that must be on the line just before it and start with `@` followed by a file name
or the special label name `@embed`.

Multi-backend Python Transpiler
-----------------

Fenced code blocks that begin with `ʽʽʽpythia` will be transpiled to C++14 (by default), and compiled with `g++`.
A single markdown file can contain multiple targets to transpile, each fenced block must have its own file name label,
and define at the start of the script which backend to transpile with.

Pythia's transpiler will check each script's first line for a special comment starting with `#backend:`, valid options are:
* `#backend:c++`
* `#backend:javascript`
* `#backend:go`

