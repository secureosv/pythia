ctypes test
-------------

note: `ctypes.CDLL('')` loads from the current process address space,
TODO what is the C name of C++ `hello_world`? even when defined with extern,
which makes the function compatible, it fails to be exported here,
or at least ctypes is unable to reach it using `ctypes.CDLL('')`

@embed
```python
import ctypes

def test_func_ptr( fptr ):
	print 'function pointer'
	print fptr

def run_test():
	print 'cpython: running test...'
	lib = ctypes.CDLL('')
	print 'ctypes lib', lib
	lib.say_hi_c()

	#lib.hello_world()
	#lib._hello_world()
	if not hasattr(lib, 'hello_world'):
		print 'hello_world C function missing'
	hw = getattr(lib, 'hello_world')  ## crashes here
	#print 'got C function'
	print hw
	#hw.restype = ctypes..
	#hw.argtypes = tuple(...)
	print 'test OK'

```

c staticlib
------
this C code gets compiled by gcc, compiled to its own staticlib, and linked into the main c++ program.
```c
#include <stdio.h>

void say_hi_c() {
	printf("Hello world from C\n");
}
```

C++ Dynamic Library
-------------------
@libmymodule
```pythia
#backend:c++ dynamiclib
with extern():
	def hello_worldXXX():
		print 'hello worldXXX'


```

Build Options
-------------
* @link:python2.7
* @include:/usr/include/python2.7
```pythia
#backend:c++
import cpython

with extern():
	def say_hi_c(): pass

	def hello_world():
		print 'hello world'

def main():
	say_hi_c()
	print 'init CPython...'
	state = cpython.initalize()

	with gil:
		#cpython.test_func_ptr( addr(hello_world) as int )
		cpython.run_test()

	cpython.finalize(state)
	print 'OK'

```