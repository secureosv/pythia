Pythia
------
Multi-language Python based transpiler, optimized for translation to: C++11 or JavaScript.

Installing
----------

run `install.sh` script as root, this will creates a symbolic link `pythia` that points to the current location of `pythia.py`.


```bash
cd
git clone https://github.com/secureosv/pythia.git
cd pythia
sudo ./install.sh
```


Using `pythia`
-----------------
To see all the command line options run `pythia --help`

```bash
pythia path/to/mymarkdown.md mybuild.tar
```


C++ Translation
---------------

* [typed backend extra syntax](https://github.com/rusthon/Rusthon/blob/master/doc/syntax.md)
* [vectors](https://github.com/rusthon/Rusthon/wiki/Lists-and-Arrays)
* [concurrency](https://github.com/rusthon/Rusthon/wiki/concurrency)
* [cpython integration](https://github.com/rusthon/Rusthon/wiki/CPython-Integration)
* [arrays and generics](https://github.com/rusthon/Rusthon/wiki/Array-Generics)
* [java frontend](https://github.com/rusthon/Rusthon/wiki/Java-Frontend)
* [memory and reference counting](https://github.com/rusthon/Rusthon/blob/master/doc/memory.md)
* [weak references](https://github.com/rusthon/Rusthon/wiki/Weak-References)
* [nim integration](https://github.com/rusthon/Rusthon/wiki/Nim-Integration)
* [c++ regression test results](https://github.com/rusthon/Rusthon/blob/master/regtests/regtest-report-c%2B%2B.md)

