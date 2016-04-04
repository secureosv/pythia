Cython Hello World
-------

@embed
```python
import os, sys
sys.path.append( os.path.curdir )  ## TODO this should not be required to import the cython module
import mycython_module as cymod

def run_test():
	cymod.hi_cython()

```


@mycython_module
```cython

def hi_cython():
	a = 'hello'
	b = 'world'
	print a + b
	cdef int x=10
	cdef int y=20
	print x + y

```

Build Options
-------------
* @link:python2.7
* @include:/usr/include/python2.7
@myexe
```pythia
#backend:c++
import cpython

def main():
	a = 'hello'
	b = 'world'
	print a + b
	x=10
	y=20
	print x + y


	print 'init CPython...'
	state = cpython.initalize()
	with gil:
		cpython.run_test()
	cpython.finalize(state)
	print 'OK'

```
