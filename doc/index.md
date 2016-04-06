installing pythia
-----------------

run `install.sh` script as root.
note: this just creates a symbolic link `pythia` that points to the current location of `pythia.py`.


```bash
cd
git clone https://github.com/secureosv/pythia.git
cd pythia
sudo ./install.sh
```


using `pythia` command line
-----------------
To see all the command line options run `pythia --help`

build and run markdown file
```bash
pythia mymarkdown.md
```

transpile python script to c++, build and run
```bash
pythia myscript.py
```

transpile python script to javascript, build and run in node.js
```bash
pythia myscript.py --javascript
```


build and save to a tar file
```bash
pythia mymarkdown.md myoutput.tar
```

use `--osv` , to package into an OSv container and run in qemu.
(requires 64bit linux)
```bash
pythia path/to/mymarkdown.md mybuild.tar  --osv
```

Markdown Containers
-------------------

The primary format `pythia` works with is markdown containers files (`.md`).
Markdown containers allow you to bundle code and data into a single file.  They store project and file directory stucture,
code build options, and code documentation.

Markdown files that contain fenced-code-blocks using github style markdown, can be compiled and run with `pythia`.
Tripple backquotes "```" are used to fence a block of code.  The start of a fence can contain a language name, like: "```c++",
this will trigger that fenced code block to be compiled with `g++`.

Fenced code blocks can also contain a label that must be on the line just before it and start with `@` followed by a file name
or the special label name `@embed`.

Python Transpiler
-----------------

Fenced code blocks that begin with "```pythia" will be transpiled to C++14 (by default), and compiled with `g++`.
A single markdown file can contain multiple targets to transpile, each fenced block must have its own file name label,
and define at the start of the script which backend to transpile with.

Pythia's transpiler will check each script's first line for a special comment starting with `#backend:`, valid options are:
* `#backend:c++`
* `#backend:javascript`
* `#backend:go`




