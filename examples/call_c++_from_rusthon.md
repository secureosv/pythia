C++ Class Example
----------------

The extra markdown syntax below `@embed:mybinary` is used to
insert the c++ code into the transpiled output.


@embed:mybinary
```c++
#include <fstream>
#include <iostream>
#include <string>

class HelloWorld {
  public:
	std::string mystring;
	void mymethod();
	void set( std::string s ) { this->mystring = s;}
};
	void HelloWorld::mymethod() {
		std::cout << this->mystring << std::endl;
	}

int mycppfunc( HelloWorld* ob ) {
	ob->mymethod();
	return 1;
}

```

`Subclass` defines `__init__` to workaround the problem of calling the parent constructor
of an external c++ class.

@mybinary
```rusthon
#backend:c++

class Subclass( HelloWorld ):
	def __init__(self, s:string ):
		self.set( s )

	def foo(self):
		print 'foo'
		return self.mystring

def main():
	## because HelloWorld is an external c++ class,
	## `new` must be used to initialize it.
	ob = new(HelloWorld())
	ob.set('hi')
	ob.mymethod()
	print ob

	## note: mycppfunc can be called directly
	## because it is embedded, and not linked
	## to an external library.
	assert mycppfunc( ob ) == 1

	## because Subclass is defined here,
	## it can be initialized without using `new`
	s1 = new Subclass('bar1')
	s2 = new(Subclass('bar2'))
	s3 = Subclass('bar3')
	print s1
	s1.mymethod()
	assert s1.foo()=='bar1'


```