
OSv image manifest
------------------
Below is the minimal set of files required to run Python and Numpy

@usr.manifest
```
/usr/lib/python2.7/site.py: /usr/lib/python2.7/site.py
/usr/lib/python2.7/os.py: /usr/lib/python2.7/os.py
/usr/lib/python2.7/posixpath.py: /usr/lib/python2.7/posixpath.py
/usr/lib/python2.7/stat.py: /usr/lib/python2.7/stat.py
/usr/lib/python2.7/genericpath.py: /usr/lib/python2.7/genericpath.py
/usr/lib/python2.7/warnings.py: /usr/lib/python2.7/warnings.py
/usr/lib/python2.7/linecache.py: /usr/lib/python2.7/linecache.py
/usr/lib/python2.7/types.py: /usr/lib/python2.7/types.py
/usr/lib/python2.7/UserDict.py: /usr/lib/python2.7/UserDict.py
/usr/lib/python2.7/_abcoll.py: /usr/lib/python2.7/_abcoll.py
/usr/lib/python2.7/abc.py: /usr/lib/python2.7/abc.py
/usr/lib/python2.7/_weakrefset.py: /usr/lib/python2.7/_weakrefset.py
/usr/lib/python2.7/copy_reg.py: /usr/lib/python2.7/copy_reg.py
/usr/lib/python2.7/traceback.py: /usr/lib/python2.7/traceback.py
/usr/lib/python2.7/sysconfig.py: /usr/lib/python2.7/sysconfig.py
/usr/lib/python2.7/re.py: /usr/lib/python2.7/re.py
/usr/lib/python2.7/sre_compile.py: /usr/lib/python2.7/sre_compile.py
/usr/lib/python2.7/sre_parse.py: /usr/lib/python2.7/sre_parse.py
/usr/lib/python2.7/sre_constants.py: /usr/lib/python2.7/sre_constants.py
/usr/lib/python2.7/_sysconfigdata.py: /usr/lib/python2.7/_sysconfigdata.py
/usr/lib/python2.7/plat-x86_64-linux-gnu/_sysconfigdata_nd.py: /usr/lib/python2.7/plat-x86_64-linux-gnu/_sysconfigdata_nd.py


/usr/lib/python2.7/string.py: /usr/lib/python2.7/string.py
/usr/lib/python2.7/shutil.py: /usr/lib/python2.7/shutil.py
/usr/lib/python2.7/io.py: /usr/lib/python2.7/io.py
/usr/lib/python2.7/weakref.py: /usr/lib/python2.7/weakref.py
/usr/lib/python2.7/fnmatch.py: /usr/lib/python2.7/fnmatch.py
/usr/lib/python2.7/pprint.py: /usr/lib/python2.7/pprint.py
/usr/lib/python2.7/difflib.py: /usr/lib/python2.7/difflib.py
/usr/lib/python2.7/StringIO.py: /usr/lib/python2.7/StringIO.py
/usr/lib/python2.7/functools.py: /usr/lib/python2.7/functools.py
/usr/lib/python2.7/heapq.py: /usr/lib/python2.7/heapq.py
/usr/lib/python2.7/keyword.py: /usr/lib/python2.7/keyword.py
/usr/lib/python2.7/collections.py: /usr/lib/python2.7/collections.py
/usr/lib/python2.7/__future__.py: /usr/lib/python2.7/__future__.py

/usr/lib/python2.7/lib-dynload/datetime.x86_64-linux-gnu.so: /usr/lib/python2.7/lib-dynload/datetime.x86_64-linux-gnu.so
/usr/lib/python2.7/lib-dynload/future_builtins.x86_64-linux-gnu.so: /usr/lib/python2.7/lib-dynload/future_builtins.x86_64-linux-gnu.so
/usr/lib/python2.7/dist-packages/numpy/**: /usr/lib/python2.7/dist-packages/numpy/**
/usr/lib/python2.7/unittest/**: /usr/lib/python2.7/unittest/**

```

Python Code
-----------

The Python script below is embedded in the final c++ exe, and run when `cpython.initalize` is called.
The `Mat` class can then be used from Rusthon using the special `->` syntax, that generates the required CPython C-API calls.

@embed
```python
import numpy

class Mat():
	def __init__(self):
		self.lst = []
		self.v1  = numpy.array([1,2,3,4]).astype(int)
		self.v2  = numpy.array([0.01,0.002,0.0003,0.000004,0.00005,6.1]).astype(float)
	def show(self):
		print 'self.lst:', self.lst
		print 'self.v1:', self.v1
		print 'self.v2:', self.v2

```

Below, example loops over numpy arrays: `v1` and `v2`, copies items from `v1` to `vec` a c++11 `std::vector` and appends them to
`m->lst` which is a normal Python array above `self.lst`.

Syntax for casting to Python Object types, `X as PYTYPE`, where PYTYPE can be:
* pyint
* pyi32
* pylong
* pyi64
* pyfloat
* pyf32
* pydouble
* pyf64
* pystring
* pybool


Build Options
-------------
* @link:python2.7
* @include:/usr/include/python2.7
```rusthon
#backend:c++
import cpython

def main():
	state = cpython.initalize()

	vec = []int()

	with gil:
		m = cpython.Mat()
		n1 = len(m->v1)
		n2 = len(m->v2)
		print 'length of vec1:', n1
		print 'length of vec2:', n2
		for i in range( len(m->v1) ):
			value = m->v1[i] as int
			print value
			vec.append(value)
			m->lst->append(i as pyint)
		m->show()
		for i in range( len(m->v2) ):
			a = m->v2[i] as float
			print a
			m->v2[i] = 3.14 as pyfloat
		m->show()

		for item as int in m->lst:
			print 'list item:', item

		m->lst->append("hello list" as pystring)
		m->lst->append(1.123456789 as pyfloat)
		m->lst->append( m )

		m->show()
		for something in m->lst:
			#print pytype(something)
			#print something->__class__->__name__ as string

			if ispyinstance(something, int):
				print 'item is a int'
				print something
			elif ispyinstance(something, str):
				print 'item is a string'
				print something
			elif ispyinstance(something, float):
				print 'item is a float'
				print something
			elif ispyinstance(something, Mat):
				print 'item is an instance of Mat'
				print something				
			else:
				print 'item is unknown some object'
				print something

	print 'length of vec copy:', len(vec)

	cpython.finalize(state)

```