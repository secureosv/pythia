
using `pythia` command line
-----------------
pythia compiles [markdown containers](markdown_format.md) into executeable packages.

to build and run a markdown container file
```bash
pythia mymarkdown.md
```

note: to see all the command line options run `pythia --help`


output c++ and run binary
-------------------------

transpile python script to c++, build and run
```bash
pythia myscript.py
```

javascript backend
------------------

transpile python script to javascript, build and run in node.js
```bash
pythia myscript.py --javascript
```

output simple tar container
----------------------------

build and save to a tar file
```bash
pythia mymarkdown.md myoutput.tar
```

OSv
------
Pythia generates containers for `OSv` a cloud optimized operating system.

http://osv.io/

use `--osv` , to package into an OSv container and run in qemu.
(requires 64bit linux)
```bash
pythia path/to/mymarkdown.md mybuild.tar  --osv
```

installing pythia on 64bix linux
--------------------------------
run `install.sh` script as root.

```bash
git clone https://github.com/secureosv/pythia.git
cd pythia
sudo ./install.sh
```

