Pythia's C++ translator requires static programs.
The static type syntax is inspired by, and borrows from: Cython, C++, Rust and Golang.

Pythia is similar to [RPython](http://rpython.readthedocs.org/en/latest/rpython.html#definition), a restricted and non-dynamic subset of Python.


static typed vectors
---------
[list and array doc](lists.md)

```go
a = []int(1,2,3)
b = []int(x for x in range(3))
```

static typed maps
---------
```go
a = map[string]int{'a':1, 'b':2}
```

map iteration
-------------
The key value pairs can be looped over with a for loop.
```python
def main():
	a = map[string]int{'x':100, 'y':200}
	b = ''
	c = 0
	for key,value in a:
		b += key
		c += value
```


async channels
--------------
https://github.com/rusthon/Rusthon/blob/master/regtests/rust/chan_universal_style.py
```python
sender, recver = channel(int)
```

<- send data
---------
```go
a <- b
```

channel select
--------------
switches to a given case when the channel data is ready.
```go
select:
	case x = <- a:
		y += x
	case x = <- b:
		y += x
```

function channel parameter types
--------------------------------
```python
def sender_wrapper( sender: chan Sender<int> ):
	sender <- 100

def recv_wrapper(recver: chan Receiver<int> ):
	result = <- recver
```


switch syntax
-------------

```javascript
switch a == b:
	case True:
		x = z
	case False:
		y = z
	default:
		break

```

JavaScript Extra Syntax
=======================

var
----
. `var ` is allowed before a variable name in an assignment.
```javascript
	var x = 1
```

new
----
. 'new' can be used to create a new JavaScript object
```python
	a = new SomeObject()
```

Jquery
----
. `$` can be used to call a function like jquery
```python
	$(selector).something( {'param1':1, 'param2':2} )
```

. External Javascript functions that use an object as the last argument for optional named arguments, can be called with Python style keyword names instead.
```python
	$(selector).something( param1=1, param2=2 )
```

. `$` can be used as a funtion parameter, and attributes can be get/set on `$`.
```python
def setup_my_jquery_class( $ ):
	$.fn.someclass = myclass_init
```



exception expressions
-------------------------------
this is a shortcut for writting simple try/except blocks that assign a value to a variable
(PEP 463)
```python
a = {}
b = a['somekey'] except KeyError: 'my-default'
```


Invalid Syntax
=======================
  . `with` is reserved for special purposes.  
  . `for/else` and `while/else` are deprecated.