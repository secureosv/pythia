installing pythia
-----------------

pythia requires 64bit linux and g++4.9 for all features and test scripts to work.

Run `install.sh` script as root.
This creates a symbolic link `pythia` that points to the current location of `pythia.py`.


```bash
cd
git clone https://github.com/secureosv/pythia.git
cd pythia
sudo ./install.sh
```

optional dependencies
-------------------
* git
* gnuplot
* cython

documentation
-------------
* [getting started](getting_started.md)
* [syntax](syntax.md)
* [seastar](seastar.md)
