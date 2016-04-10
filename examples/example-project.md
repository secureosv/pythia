Multilanguage Markdown Containers
=================================

pythia.py can be given a markdown file `.md` and code blocks will be extracted and compiled.
This is inspired by CoffeeScript literate format, http://coffeescript.org/#literate

Fenced code blocks with the syntax highlight tag are used to translate and build the project,
the supported languages are: `pythia`, `c++`, `rust`, `javascript`, `python`
Code blocks tagged as `javascript` or `python` are saved to the output tar file.
Fenced code blocks without a syntax highlight tag are ignored.

c++ example
-----------
the function below `say_hi_cpp` can be directly called from the pythia code below,
because the default backend for pythia is c++.

@embed:mybin
```c++
#include <fstream>
#include <iostream>
#include <string>
void say_hi_cpp() {
	std::cout << std::string("hello world from c++") << std::endl;
}
```

pythia script
----------
The code below is translated to C++ and merged with the hand written C++ code above.

@mybin
```pythia
def say_hi():
	print( 'hello world')

def main():
	say_hi()
	say_hi_cpp()
```

python2 script
-------------
```python
print('cpython script')
```

javascript
-------
```javascript
window.alert('hi');
```

go
-------
This hand written Go code is callable from the pythia code below.

@embed:mygobin
```go
func my_go_func() {
	fmt.Println("hello world from Go.")
}
func call_pythia_func_from_go() {
	my_pythia_func()
}
```

pythia go backend
------------------
The backend is selected by the special comment on the first line of the script,
below the Go backend is set by `#backend:go`.
When using the Go backend, hand written Go code can be called directly,
the call below `my_go_func` is defined above.

@mygobin
```pythia
#backend:go

def my_pythia_func():
	print('my pythia func called from go')

def main():
	print('hello from pythia go backend')
	my_go_func()
	call_pythia_func_from_go()
```

