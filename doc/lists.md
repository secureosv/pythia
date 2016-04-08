When transpiled to C++14 lists `[]` are converted to a vector of a single element type.  In regular python you are allowed to create a list that contains different types, like: `[1, "foo", 2.2]`, this is not allowed in Pythia because the list must be translated into a C++11 vector type `std::vector<T>` (where `T` is the element type).  Lists and other container types are restricted in this way, and follows closely the [RPython language spec](http://rpython.readthedocs.org/en/latest/rpython.html#object-restrictions).

invalid list
------------
lists of multiple types are not allowed
```python
a = [100, "mystring", 99.9999]
```

integer list
------------
if the type of a list can be inferred from its arguments, 
then regular python syntax can be used to create it,
otherwise the syntax `[]int(...)` must be used.

```python
a = [1,2,3]
b = []int()
c = []int(1,2,3)
```

fixed size arrays
-----------------
in stack mode a fixed size array is allocated as a low level C array,
and new items can not be appended to it. 
```python
with stack:
	a = [2]int()
	a[0] = 100
	a[1] = 2500
```

multi dimensional lists
-----------------------
```python
a = [][]int()
a.append( [1,2,3] )
a.append( [3,4,5] )
assert a[0][0]==1
assert a[1][2]==5
```

slicing lists
-------------
when slicing a list the slice must be assigned to a variable,
passing a slice directly in a function call `f( a[1:2] )` is not allowed.

```python
myslice = mylist[ 10:2 ]
f( myslice )
```
