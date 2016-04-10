Pythia
------
Multi-language compiler frontend and Python based transpiler, integrated with OSv, and optimized for translation to: C++14 and JavaScript.
Pythia can translate Python scripts (`.py` files), and multi-language/multi-data projects contained in Markdown (`.md` files).

[documentation](http://pythia.readthedocs.org/en/latest/)

[examples](http://secureosv.github.io/pythia/)


C++ Example
-----------
The C++ translator can convert Python directly into C++14, most of the time line by line,
without any magic.

```python

def foo( a ):
	return a + 1

def main():
	x = foo(2)
	assert x==3

```

The translator output is made more human readable by using `auto` to make the C++ compiler guess the type of `a` and return type of `foo`
```c++
auto foo(auto a) {
	return (a + 1);
}
int main() {
	auto x = foo(2);
	if (!(( x == 3 ))) {throw std::runtime_error("assertion failed: ( x == 3 )"); }
	return 0;
}
```

Javascript Example
------------------

The same example above is translated into this Javascript.
```javascript
var foo =  function foo(a){
	return (a + 1);
}

var main =  function main(){
	var x;
	x = foo(2);
	if (!(x === 3)) {throw new Error("assertion failed"); }
}
```

old wiki
---------------
* [vectors](https://github.com/rusthon/Rusthon/wiki/Lists-and-Arrays)
* [concurrency](https://github.com/rusthon/Rusthon/wiki/concurrency)
* [cpython integration](https://github.com/rusthon/Rusthon/wiki/CPython-Integration)
* [arrays and generics](https://github.com/rusthon/Rusthon/wiki/Array-Generics)
* [java frontend](https://github.com/rusthon/Rusthon/wiki/Java-Frontend)
* [weak references](https://github.com/rusthon/Rusthon/wiki/Weak-References)
* [nim integration](https://github.com/rusthon/Rusthon/wiki/Nim-Integration)
