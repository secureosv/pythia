pysam
-------
install with:
	`pip install pysam`

ported from:
	http://pysam.readthedocs.org/en/latest/usage.html#usage

run:
```bash
pythia examples/cpython_pysam.md
cat /tmp/test.bam
```


OSv image manifest
------------------
Below is the minimal set of files required to run Python and Pysam

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

/usr/local/lib/python2.7/dist-packages/pysam/**: /usr/local/lib/python2.7/dist-packages/pysam/**
/usr/lib/python2.7/tempfile.py: /usr/lib/python2.7/tempfile.py
/usr/lib/python2.7/random.py: /usr/lib/python2.7/random.py
/usr/lib/python2.7/hashlib.py: /usr/lib/python2.7/hashlib.py

/usr/lib/python2.7/bisect.py: /usr/lib/python2.7/bisect.py
/usr/lib/python2.7/codecs.py: /usr/lib/python2.7/codecs.py
/usr/lib/python2.7/encodings/ascii.py: /usr/lib/python2.7/encodings/ascii.py

/usr/lib/python2.7/xml/**: /usr/lib/python2.7/xml/**
/usr/lib/python2.7/lib-dynload/_elementtree.x86_64-linux-gnu.so: /usr/lib/python2.7/lib-dynload/_elementtree.x86_64-linux-gnu.so
/usr/lib/python2.7/lib-dynload/pyexpat.x86_64-linux-gnu.so: /usr/lib/python2.7/lib-dynload/pyexpat.x86_64-linux-gnu.so
/usr/lib/libexpat.so.1: /lib/x86_64-linux-gnu/libexpat.so.1

/usr/lib/python2.7/copy.py: /usr/lib/python2.7/copy.py
/usr/lib/python2.7/base64.py: /usr/lib/python2.7/base64.py
/usr/lib/python2.7/struct.py: /usr/lib/python2.7/struct.py


```

Python Code
-----------


@embed
```python
import pysam

header = { 
	'HD': {'VN': '1.0'},
	'SQ': [
		{'LN': 1575, 'SN': 'chr1'},
		{'LN': 1584, 'SN': 'chr2'}
	] 
}

def test_pysam():
	with pysam.AlignmentFile('/tmp/test.bam', "wb", header=header) as outf:
		a = pysam.AlignedSegment()
		a.query_name = "read_28833_29006_6945"
		a.query_sequence="AGCTTAGCTAGCTACCTATATCTTGGTCTTGGCCG"
		a.flag = 99
		a.reference_id = 0
		a.reference_start = 32
		a.mapping_quality = 20
		a.cigar = ((0,10), (2,1), (0,25))
		a.next_reference_id = 0
		a.next_reference_start=199
		a.template_length=167
		a.query_qualities = pysam.qualitystring_to_array("<<<<<<<<<<<<<<<<<<<<<:<9/,&,22;;<<<")
		a.tags = (("NM", 1),("RG", "L1"))
		outf.write(a)

```


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
		res = cpython.test_pysam()

	cpython.finalize(state)

```