Embed CPython
-------------

To run in OSv
```
cd pythia/examples
pythia hello_cpython.md --osv
```

This example directly uses the Python CAPI, for more info on embedding Python, see [here](https://docs.python.org/2.7/extending/embedding.html)

The syntax below `* @link:` allows you to list external pre-built libraries to link to.
The syntax `* @include:` allows you to list directories for GCC to find external header files,
and include them in the final build using `import myheader.h`.

note requires: static library `libpython.a`

OSv image manifest
------------------
extra files copied into the VM image

note: using `/usr/lib/python2.7/**: /usr/lib/python2.7/**` copies everything,
but takes a really long time. Below is the minimal set of files required to run Python.


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


```

Build Options
-------------
* @link:python2.7
* @include:/usr/include/python2.7
```rusthon
#backend:c++
import Python.h

with pointers:
	def unbox( pyob:PyObject ) -> int:
		a = PyInt_AS_LONG(pyob)
		return a as int

pyhome = None
def main():
	print '************************'
	print Py_GetProgramName()
	Py_Initialize()
	print 'pyinit ok'
	PyRun_SimpleString(cstr("result = 1+2"))
	mod = PyImport_AddModule(cstr("__main__"))
	mdict = PyModule_GetDict(mod)
	result = PyDict_GetItemString(mdict, cstr("result"))
	x = unbox( result )
	print x
	Py_Finalize()
	print 'Python2.7 hello world complete'

```