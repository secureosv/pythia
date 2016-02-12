pymzML
-------
install with:
	`pip install pymzml`

download `small.pwiz.1.1.mzML` to `/tmp/`:
	http://proteowizard.sourceforge.net/example_data/small.pwiz.1.1.mzML

ported from:
	https://github.com/pymzml/pymzML/blob/master/example_scripts/polarity.py



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


@embed
```python
import pymzml

verbose = True
def test_pymzml():
	print 'testing pymzml...'
	example_file = open('/tmp/small.pwiz.1.1.mzML', 'rb')
	print example_file
	run = pymzml.run.Reader(
		example_file,
		MSn_Precision = 250e-6,
		obo_version = '1.1.0',
		extraAccessions = [
			('MS:1000129',['value']),
			('MS:1000130',['value'])
		]
	)
	print 'spec list:', run

	for spec in run:
		print spec
		negative_polarity = spec.get('MS:1000129', False)
		if negative_polarity == '':
			negative_polarity = True
		positive_polarity = spec.get('MS:1000130', False)
		if positive_polarity == '':
			positive_polarity = True
		print(
			'Polarity negative {0} - Polarity positive {1}'.format(
				negative_polarity,
				positive_polarity
			)
		)

	print 'ok'

```

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

	with gil:
		res = cpython.test_pymzml()

	cpython.finalize(state)

```