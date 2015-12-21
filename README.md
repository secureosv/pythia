Pythia
------
Multi-language Python based transpiler, integrated with OSv, and optimized for translation to: C++14 and JavaScript.

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
The option `--osv` will package your app into an OSv image container.
```bash
pythia path/to/mymarkdown.md mybuild.tar  --osv
```

Quick Example
-------------
Pythia extends normal Python with syntax from C++, and simplifies calling and chaining lambda functions.
The new syntax below `and then():` chains a new lambda function to the previous one.
The functions are defined under `with stack:` are set to use stack memory mode (CPU Cache).
The default memory mode is the heap (RAM).

```python

with stack:
	def delay(seconds) -> future<>:
		print 'sleeping', seconds
		sleep(seconds)
		return future

	def f() -> future<>:
		delay(1) and then():
			print 'sleep1'
			and then():
				print 'sleep1.1'
				delay(1) and then():
					print 'nested 1.1:1'
					and then():
						print 'nested 1.1:2'

			and then():
				print 'sleep1.2'
				and then():
					print 'sleep1.2.1'

		delay(2) and then():
			print 'sleep2'

		return delay(3) and then():
			print 'all done'

```


C++14 Backend Docs
---------------
Pythia extends the Rusthon C++11 backend to support C++14, with specialized syntax for using the SeaStar 
high performance asyc IO framework.  The C++14 backend makes static typing optional, and allows you to write python like scripts that are compiled to fast native code.


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

