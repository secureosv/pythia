C++11 Backend Regression Tests
-----------------------------
the following tests compiled, and the binary executed without any errors
* [pointers_returns_array2D.py](c++/pointers_returns_array2D.py)

input:
------
```python
'''
returns array of arrays
'''

with pointers:
	def make_array() -> [][]int:
		arr = new(
			[][]int(
				(1,2,3),
				(4,5,6,7,8)
			)
		)
		return arr

	def test_array( arr:[][]int ):
		print( arr[0][0] )

	def main():
		a = make_array()
		print( len(a))
		print( len(a[0]) )
		print( len(a[1]) )

		test_array(a)
```
output:
------
```c++

std::vector<std::vector<int>*>* make_array() {

	
	auto arr = (new std::vector<std::vector<int>*> {new std::vector<int> {1,2,3},new std::vector<int> {4,5,6,7,8}});			/* new variable */
	return arr;
}
void test_array(std::vector<std::vector<int>*>* arr) {

	
	std::cout << (*(*arr)[0])[0] << std::endl;
	/* arrays:
		arr : [][]int
*/
}
int main() {

	
	auto a = make_array();			/* new variable */
	std::cout << a->size() << std::endl;
	std::cout << (*a)[0]->size() << std::endl;
	std::cout << (*a)[1]->size() << std::endl;
	test_array(a);
	return 0;
}
```
* [pointers_returns_array.py](c++/pointers_returns_array.py)

input:
------
```python
'''
returns array of arrays
'''

with pointers:
	def make_array() -> []int:
		arr = new([]int( 1,2,3,4 ))
		return arr

	def test_array( arr:[]int ):
		print( arr[0] )
		print( arr[1] )
		print( arr[2] )
		print( arr[3] )

	def main():
		a = make_array()
		print('arr length:', len(a))
		test_array(a)
```
output:
------
```c++

std::vector<int>* make_array() {

	
	auto arr = (new std::vector<int> {1,2,3,4});			/* new variable */
	return arr;
}
void test_array(std::vector<int>* arr) {

	
	std::cout << (*arr)[0] << std::endl;
	std::cout << (*arr)[1] << std::endl;
	std::cout << (*arr)[2] << std::endl;
	std::cout << (*arr)[3] << std::endl;
	/* arrays:
		arr : []int
*/
}
int main() {

	
	auto a = make_array();			/* new variable */
	std::cout << std::string("arr length:");
std::cout << a->size();std::cout << std::endl;
	test_array(a);
	return 0;
}
```
* [chan.py](c++/chan.py)

input:
------
```python
"""cpp-channel backend - send int over channel"""

def sender_wrapper(a:int, send: chan int ):
	## `chan T` is an alias for `cpp::channel<T>`
	print 'sending'
	result = 100
	send <- result

def recv_wrapper(a:int, recver: cpp::channel<int> ) -> int:
	## above namespace and template are given c++ style to recver
	print 'receiving'
	v = <- recver
	return v

def main():
	print 'enter main'
	c = channel(int)  ## `channel(T)` translates to: `cpp::channel<T>`
	print 'new channel'
	## spawn creates a new std::thread, 
	## and joins it at the end of the function.
	print 'doing spawn thread'
	spawn( sender_wrapper(17, c) )
	print 'done spawning thread'
	# Do other work...
	x = recv_wrapper(2, c)
	print(x)
	assert x==100
	print 'ok'
```
output:
------
```c++

void sender_wrapper(int a, cpp::channel<int>  send) {

	
	std::cout << std::string("sending") << std::endl;
	auto result = 100;  /* auto-fallback */
	send.send(result);
}
int recv_wrapper(int a, cpp::channel<int> recver) {

	
	std::cout << std::string("receiving") << std::endl;
	auto v = recver.recv();
	return v;
}
int main() {

	
	std::cout << std::string("enter main") << std::endl;
	auto c = cpp::channel<int>{};			/* new variable */
	std::cout << std::string("new channel") << std::endl;
	std::cout << std::string("doing spawn thread") << std::endl;
	std::thread __thread0__( [&]{sender_wrapper(17, c);} );
	std::cout << std::string("done spawning thread") << std::endl;
	auto x = recv_wrapper(2, c);			/* new variable */
	std::cout << x << std::endl;
	if (!(( x == 100 ))) {throw std::runtime_error("assertion failed: ( x == 100 )"); }
	std::cout << std::string("ok") << std::endl;
	if (__thread0__.joinable()) __thread0__.join();
	return 0;
}
```
* [named_params.py](c++/named_params.py)

input:
------
```python
'''
keyword arguments
'''

def f1( a=1 ) -> int:
	return a*2

## this break rust because the global kwargs-type then requires `b` and `__use__b`
## but the caller only gives `a` and `__use__a`
def f2( a=1, b=2 ) -> int:
	return a + b

def main():
	print( f1(a=100) )
	#print( f2(a=100, b=200) )  ## TODO fix in c++
```
output:
------
```c++

int f1(_KwArgs_*  __kwargs) {

	int  a = 1;
	if (__kwargs->__use__a == true) {
	  a = __kwargs->_a_;
	}
	
	return (a * 2);
}
int f2(_KwArgs_*  __kwargs) {

	int  a = 1;
	if (__kwargs->__use__a == true) {
	  a = __kwargs->_a_;
	}
	int  b = 2;
	if (__kwargs->__use__b == true) {
	  b = __kwargs->_b_;
	}
	
	return (a + b);
}
int main() {

	
	std::cout << f1((new _KwArgs_())->a(100)) << std::endl;
	return 0;
}
```
* [array_slice.py](c++/array_slice.py)

input:
------
```python
'''
array slice syntax
'''

def somefunc():
	for step in range(2):
		w = range(10)
		assert len(w)==10
		assert w[0]==0
		assert w[9]==9

		r = range(10,20)
		assert r[0]==10
		assert r[1]==11

		a = [1,2,3,4,5]
		print('a addr:', a)
		print('len a:', len(a))
		assert len(a)==5
		b = a[1:]
		print('b addr (should not be `a` above):', b)
		print('len b  (should be 4):', len(b))
		assert len(b)==4

		c = a[:]
		print('c addr (should not be `a` or `b` above):', c)
		print('len c:', len(c))
		assert len(a)==len(c)
		c.append(6)
		print('len c - after append:', len(c))
		assert len(c)==6
		assert len(a)==5

		d = a[:2]
		print('len d:', len(d))
		assert len(d)==2
		assert d[0]==1
		assert d[1]==2

		print('len a:', len(a))
		e = a[::1]
		print('len e should be same as a:', len(e))
		assert len(e)==len(a)
		for i in e: print i

		f = a[::2]
		print('len f:', len(f))
		assert len(f)==3
		assert f[0]==1
		assert f[1]==3
		assert f[2]==5

		g = a[::-1]
		print '- - - -'
		for v in g:
			print v

		print('len g:', len(g))
		assert len(g)==len(a)


		assert g[0]==5
		assert g[4]==1
		#for i in g: print i

		print('---slice---')
		h = a[2::-1]
		for i in h: print i
		print('len h:', len(h))
		assert len(h)==3

		assert h[0]==3
		assert h[1]==2
		assert h[2]==1
		print('h.append')
		h.append(1000)
		h.append(1000)
		print('len h after:', len(h))
		assert len(h)==5
		#assert h[-1]==1000  ## TODO fixme
		assert h[3]==1000
		assert h[4]==1000

		#assert h.back==1000
		print('---slice assignment---')

		a[:1+1] = h
		#for i in a: print i
		print('len a:', len(a))
		assert len(a)==8

	print('somefunc done')

def main():
	print('calling somefunc')
	somefunc()

	## never reached because there is a segfault at the end
	## of somefunc when the slices go out of scope, they are free'ed twice.
	print('OK')

#main()
```
output:
------
```c++

void somefunc() {

	
	for (int step=0; step<2; step++) {
		auto w = range1(10);			/* new variable */
		if (!(( w->size() == 10 ))) {throw std::runtime_error("assertion failed: ( w->size() == 10 )"); }
		if (!(( (*w)[0] == 0 ))) {throw std::runtime_error("assertion failed: ( (*w)[0] == 0 )"); }
		if (!(( (*w)[9] == 9 ))) {throw std::runtime_error("assertion failed: ( (*w)[9] == 9 )"); }
		auto r = range2(10, 20);			/* new variable */
		if (!(( (*r)[0] == 10 ))) {throw std::runtime_error("assertion failed: ( (*r)[0] == 10 )"); }
		if (!(( (*r)[1] == 11 ))) {throw std::runtime_error("assertion failed: ( (*r)[1] == 11 )"); }
		std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
		std::cout << std::string("a addr:");
std::cout << a;std::cout << std::endl;
		std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
		if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
		/* <slice> 1 : None : None */
std::vector<int> _ref_b(
a->begin()+1,
a->end()
);
std::shared_ptr<std::vector<int>> b = std::make_shared<std::vector<int>>(_ref_b);
		std::cout << std::string("b addr (should not be `a` above):");
std::cout << b;std::cout << std::endl;
		std::cout << std::string("len b  (should be 4):");
std::cout << b->size();std::cout << std::endl;
		if (!(( b->size() == 4 ))) {throw std::runtime_error("assertion failed: ( b->size() == 4 )"); }
		/* <slice> None : None : None */
std::vector<int> _ref_c(
a->begin(),
a->end()
);
std::shared_ptr<std::vector<int>> c = std::make_shared<std::vector<int>>(_ref_c);
		std::cout << std::string("c addr (should not be `a` or `b` above):");
std::cout << c;std::cout << std::endl;
		std::cout << std::string("len c:");
std::cout << c->size();std::cout << std::endl;
		if (!(( a->size() == c->size() ))) {throw std::runtime_error("assertion failed: ( a->size() == c->size() )"); }
		c->push_back(6);
		std::cout << std::string("len c - after append:");
std::cout << c->size();std::cout << std::endl;
		if (!(( c->size() == 6 ))) {throw std::runtime_error("assertion failed: ( c->size() == 6 )"); }
		if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
		/* <slice> None : 2 : None */
std::vector<int> _ref_d(
a->begin(),
a->begin()+2
);
std::shared_ptr<std::vector<int>> d = std::make_shared<std::vector<int>>(_ref_d);
		std::cout << std::string("len d:");
std::cout << d->size();std::cout << std::endl;
		if (!(( d->size() == 2 ))) {throw std::runtime_error("assertion failed: ( d->size() == 2 )"); }
		if (!(( (*d)[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*d)[0] == 1 )"); }
		if (!(( (*d)[1] == 2 ))) {throw std::runtime_error("assertion failed: ( (*d)[1] == 2 )"); }
		std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
		/* <slice> None : None : 1 */
std::vector<int> _ref_e;
if(1<0){for(int _i_=a->size()-1;_i_>=0;_i_+=1){ _ref_e.push_back((*a)[_i_]);}} else {for(int _i_=0;_i_<a->size();_i_+=1){ _ref_e.push_back((*a)[_i_]);}}
std::shared_ptr<std::vector<int>> e = std::make_shared<std::vector<int>>(_ref_e);
		std::cout << std::string("len e should be same<<__as__<<a:");
std::cout << e->size();std::cout << std::endl;
		if (!(( e->size() == a->size() ))) {throw std::runtime_error("assertion failed: ( e->size() == a->size() )"); }
		for (auto &i: (*e)) {
			std::cout << i << std::endl;
		}
		/* <slice> None : None : 2 */
std::vector<int> _ref_f;
if(2<0){for(int _i_=a->size()-1;_i_>=0;_i_+=2){ _ref_f.push_back((*a)[_i_]);}} else {for(int _i_=0;_i_<a->size();_i_+=2){ _ref_f.push_back((*a)[_i_]);}}
std::shared_ptr<std::vector<int>> f = std::make_shared<std::vector<int>>(_ref_f);
		std::cout << std::string("len f:");
std::cout << f->size();std::cout << std::endl;
		if (!(( f->size() == 3 ))) {throw std::runtime_error("assertion failed: ( f->size() == 3 )"); }
		if (!(( (*f)[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*f)[0] == 1 )"); }
		if (!(( (*f)[1] == 3 ))) {throw std::runtime_error("assertion failed: ( (*f)[1] == 3 )"); }
		if (!(( (*f)[2] == 5 ))) {throw std::runtime_error("assertion failed: ( (*f)[2] == 5 )"); }
		/* <slice> None : None : -1 */
		std::vector<int> _ref_g;
for(int _i_=a->size()-1;_i_>=0;_i_-=1){
 _ref_g.push_back((*a)[_i_]);
}
std::shared_ptr<std::vector<int>> g = std::make_shared<std::vector<int>>(_ref_g);
		std::cout << std::string("- - - -") << std::endl;
		for (auto &v: (*g)) {
			std::cout << v << std::endl;
		}
		std::cout << std::string("len g:");
std::cout << g->size();std::cout << std::endl;
		if (!(( g->size() == a->size() ))) {throw std::runtime_error("assertion failed: ( g->size() == a->size() )"); }
		if (!(( (*g)[0] == 5 ))) {throw std::runtime_error("assertion failed: ( (*g)[0] == 5 )"); }
		if (!(( (*g)[4] == 1 ))) {throw std::runtime_error("assertion failed: ( (*g)[4] == 1 )"); }
		std::cout << std::string("---slice---") << std::endl;
		/* <slice> 2 : None : -1 */
		std::vector<int> _ref_h;
for(int _i_=2;_i_>=0;_i_-=1){
 _ref_h.push_back((*a)[_i_]);
}
std::shared_ptr<std::vector<int>> h = std::make_shared<std::vector<int>>(_ref_h);
		for (auto &i: (*h)) {
			std::cout << i << std::endl;
		}
		std::cout << std::string("len h:");
std::cout << h->size();std::cout << std::endl;
		if (!(( h->size() == 3 ))) {throw std::runtime_error("assertion failed: ( h->size() == 3 )"); }
		if (!(( (*h)[0] == 3 ))) {throw std::runtime_error("assertion failed: ( (*h)[0] == 3 )"); }
		if (!(( (*h)[1] == 2 ))) {throw std::runtime_error("assertion failed: ( (*h)[1] == 2 )"); }
		if (!(( (*h)[2] == 1 ))) {throw std::runtime_error("assertion failed: ( (*h)[2] == 1 )"); }
		std::cout << std::string("h.append") << std::endl;
		h->push_back(1000);
		h->push_back(1000);
		std::cout << std::string("len h after:");
std::cout << h->size();std::cout << std::endl;
		if (!(( h->size() == 5 ))) {throw std::runtime_error("assertion failed: ( h->size() == 5 )"); }
		if (!(( (*h)[3] == 1000 ))) {throw std::runtime_error("assertion failed: ( (*h)[3] == 1000 )"); }
		if (!(( (*h)[4] == 1000 ))) {throw std::runtime_error("assertion failed: ( (*h)[4] == 1000 )"); }
		std::cout << std::string("---slice assignment---") << std::endl;
		if ((1 + 1) >= a->size()) { a->erase(a->begin(), a->end());
} else { a->erase(a->begin(), a->begin()+(1 + 1)); }
a->insert(a->begin(), h->begin(), h->end());
		std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
		if (!(( a->size() == 8 ))) {throw std::runtime_error("assertion failed: ( a->size() == 8 )"); }
	}
	std::cout << std::string("somefunc done") << std::endl;
	/* arrays:
		a : int
		c : int
		b : int
		e : int
		d : int
		g : int
		f : int
		h : int
		r : int
		w : int
*/
}
int main() {

	
	std::cout << std::string("calling somefunc") << std::endl;
	somefunc();
	std::cout << std::string("OK") << std::endl;
	return 0;
}
```
* [print_classname.py](c++/print_classname.py)

input:
------
```python
'''
returns subclasses
'''
class A:
	def __init__(self, x:int):
		self.x = x

	def method(self) -> int:
		return self.x

class B(A):

	def foo(self) ->int:
		return self.x * 2

class C(A):

	def bar(self) ->int:
		return self.x + 200


def main():
	a = A(0)
	b = B(1)
	c = C(2)
	print(a.getclassname())
	print(b.getclassname())
	print(c.getclassname())


```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  x;
	A* __init__(int x);
	int method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x']
	int foo();
	B* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x']
	int bar();
	C* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
	C* C::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int C::bar() {

		
		return (this->x + 200);
	}
	B* B::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int B::foo() {

		
		return (this->x * 2);
	}
	int A::method() {

		
		return this->x;
	}
	A* A::__init__(int x) {

		
		this->x = x;
		return this;
	}
int main() {

	
	auto a = std::shared_ptr<A>((new A())->__init__(0)); // new object
	auto b = std::shared_ptr<B>((new B())->__init__(1)); // new object
	auto c = std::shared_ptr<C>((new C())->__init__(2)); // new object
	std::cout << a->getclassname() << std::endl;
	std::cout << b->getclassname() << std::endl;
	std::cout << c->getclassname() << std::endl;
	return 0;
}
```
* [array_sized.py](c++/array_sized.py)

input:
------
```python
'''
array with default size
'''

class A:
	pass

def somefunc():
	a = [5]int(1,2,3,4,5)
	print('len a:', len(a))
	a.pop()
	print('len a:', len(a))
	print(a[0])
	print(a[1])

	b = [10]int()
	print('len b:', len(b))
	print b[0]
	print b[1]

	c = [10]f64( 1.1, 2.2, 3.3 )
	print c[0]
	print c[1]
	print c[2]

	x = A()
	y = A()
	d = [4]A( x,y )
	print d[0]
	print d[1]

def stackfunc():
	with stack:
		a = [5]int(1,2,3,4,5)
		print('sizeof a:', sizeof(a))  ## says 20 bytes?
		#a.pop()  ## not possible for stack allocated fixed size arrays
		print('len a:', len(a))   ## translator keeps track of the array size
		print(a[0])
		print(a[1])
		print 'testing iter loop'
		for val in a:
			print val
		print 'slice fixed size array front'
		b = a[1:]
		assert b[0]
		assert len(b)==len(a)-1
		for val in b:
			print val
		assert b[0]==2
		assert b[1]==3
		assert b[2]==4
		assert b[3]==5
		print 'slice fixed size array back'
		c = a[:2]
		assert len(c)==2
		for val in c:
			print val
		assert c[0]==1
		assert c[1]==2

		for N in range(4, 10):
			d = [N]int()
			for i in range(N):
				d[i]=100 + i
			print d

			# sizeof(d) -> warning: taking sizeof array of runtime bound
			print 'sizeof:', sizeof(d)

			print 'len d:', len(d)
			for v in d:
				print v

			print 'slice front'
			e = d[2:]
			print e
			for ev in e:
				print ev
			assert e[0]==102
			assert e[1]==103

			print 'len e:', len(e)
			for index in range(len(e)):
				e[index]=1000+index
			assert e[0]==1000
			print 'slice back'
			f = d[:2]
			print f
			assert f[0]==100
			assert f[1]==101

def main():
	somefunc()
	stackfunc()
	print('OK')
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
void somefunc() {

	
	std::vector<int> _ref_a = {1,2,3,4,5};_ref_a.resize(5);std::shared_ptr<std::vector<int>> a = std::make_shared<std::vector<int>>(_ref_a);
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	a->pop_back();
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	std::cout << (*a)[0] << std::endl;
	std::cout << (*a)[1] << std::endl;
	std::vector<int> _ref_b = {};_ref_b.resize(10);std::shared_ptr<std::vector<int>> b = std::make_shared<std::vector<int>>(_ref_b);
	std::cout << std::string("len b:");
std::cout << b->size();std::cout << std::endl;
	std::cout << (*b)[0] << std::endl;
	std::cout << (*b)[1] << std::endl;
	std::vector<f64> _ref_c = {1.1,2.2,3.3};_ref_c.resize(10);std::shared_ptr<std::vector<f64>> c = std::make_shared<std::vector<f64>>(_ref_c);
	std::cout << (*c)[0] << std::endl;
	std::cout << (*c)[1] << std::endl;
	std::cout << (*c)[2] << std::endl;
	auto x = std::shared_ptr<A>(new A()); // new object
	auto y = std::shared_ptr<A>(new A()); // new object
	std::vector<std::shared_ptr<A>> _ref_d = {x,y};_ref_d.resize(4);std::shared_ptr<std::vector<std::shared_ptr<A>>> d = std::make_shared<std::vector<std::shared_ptr<A>>>(_ref_d);
	std::cout << (*d)[0] << std::endl;
	std::cout << (*d)[1] << std::endl;
	/* arrays:
		a : ('int', '5')
		c : ('f64', '10')
		b : ('int', '10')
		d : ('A', '4')
*/
}
void stackfunc() {

	
		int a[5] = {1,2,3,4,5};
	std::cout << std::string("sizeof a:");
std::cout << sizeof(a);std::cout << std::endl;
	std::cout << std::string("len a:");
std::cout << 5;std::cout << std::endl;
	std::cout << a[0] << std::endl;
	std::cout << a[1] << std::endl;
	std::cout << std::string("testing iter loop") << std::endl;
	for (int __idx=0; __idx<5; __idx++) {
	int val = a[__idx];
		std::cout << val << std::endl;
	}
	std::cout << std::string("slice fixed size array front") << std::endl;
	/* <fixed size slice> 1 : None : None */
	int b[4] = {a[1],a[2],a[3],a[4]};
	if (!(b[0])) {throw std::runtime_error("assertion failed: b[0]"); }
	if (!(( 4 == ( (5 - 1) ) ))) {throw std::runtime_error("assertion failed: ( 4 == ( (5 - 1) ) )"); }
	for (int __idx=0; __idx<4; __idx++) {
	int val = b[__idx];
		std::cout << val << std::endl;
	}
	if (!(( b[0] == 2 ))) {throw std::runtime_error("assertion failed: ( b[0] == 2 )"); }
	if (!(( b[1] == 3 ))) {throw std::runtime_error("assertion failed: ( b[1] == 3 )"); }
	if (!(( b[2] == 4 ))) {throw std::runtime_error("assertion failed: ( b[2] == 4 )"); }
	if (!(( b[3] == 5 ))) {throw std::runtime_error("assertion failed: ( b[3] == 5 )"); }
	std::cout << std::string("slice fixed size array back") << std::endl;
	/* <fixed size slice> None : 2 : None */
	int c[3] = {a[0],a[1]};
	if (!(( 2 == 2 ))) {throw std::runtime_error("assertion failed: ( 2 == 2 )"); }
	for (int __idx=0; __idx<2; __idx++) {
	int val = c[__idx];
		std::cout << val << std::endl;
	}
	if (!(( c[0] == 1 ))) {throw std::runtime_error("assertion failed: ( c[0] == 1 )"); }
	if (!(( c[1] == 2 ))) {throw std::runtime_error("assertion failed: ( c[1] == 2 )"); }
	for (int N=4; N<10; N++) {
		int d[N] = {};
		for (int i=0; i<N; i++) {
			d[i] = (100 + i);
		}
		std::cout << d << std::endl;
		std::cout << std::string("sizeof:");
std::cout << sizeof(d);std::cout << std::endl;
		std::cout << std::string("len d:");
std::cout << N;std::cout << std::endl;
		for (int __idx=0; __idx<N; __idx++) {
		int v = d[__idx];
			std::cout << v << std::endl;
		}
		std::cout << std::string("slice front") << std::endl;
		/* <fixed size slice> 2 : None : None */
		int e[N-2];
		int __L = 0;
		for (int __i=2; __i<N; __i++) {
		  e[__L] = d[__i];
		  __L ++;
		}
		std::cout << e << std::endl;
		for (int __idx=0; __idx<N-2; __idx++) {
		int ev = e[__idx];
			std::cout << ev << std::endl;
		}
		if (!(( e[0] == 102 ))) {throw std::runtime_error("assertion failed: ( e[0] == 102 )"); }
		if (!(( e[1] == 103 ))) {throw std::runtime_error("assertion failed: ( e[1] == 103 )"); }
		std::cout << std::string("len e:");
std::cout << N-2;std::cout << std::endl;
		for (int index=0; index<N-2; index++) {
			e[index] = (1000 + index);
		}
		if (!(( e[0] == 1000 ))) {throw std::runtime_error("assertion failed: ( e[0] == 1000 )"); }
		std::cout << std::string("slice back") << std::endl;
		/* <fixed size slice> None : 2 : None */
		int f[2];
		int __U = 0;
		for (int __i=0; __i<2; __i++) {
		  f[__U] = d[__i];
		  __U ++;
		}
		std::cout << f << std::endl;
		if (!(( f[0] == 100 ))) {throw std::runtime_error("assertion failed: ( f[0] == 100 )"); }
		if (!(( f[1] == 101 ))) {throw std::runtime_error("assertion failed: ( f[1] == 101 )"); }
	}
	/* arrays:
		a : ('int', '5')
		c : ('int', '2')
		b : ('int', '4')
		e : ('int', 'N-2')
		d : ('int', 'N')
		f : ('int', 'N-2')
*/
}
int main() {

	
	somefunc();
	stackfunc();
	std::cout << std::string("OK") << std::endl;
	return 0;
}
```
* [generics.py](c++/generics.py)

input:
------
```python
'''
generic functions
'''

def myfunc( x:int ):
	print( x * 100 )

def myfunc( x:string ):
	print( x + 'world' )

def main():
	myfunc( 10 )
	myfunc( 'hello' )
```
output:
------
```c++

void myfunc(int x) {

	
	std::cout << (x * 100) << std::endl;
}
void myfunc(std::string x) {

	
	std::cout << (x + std::string("world")) << std::endl;
}
int main() {

	
	myfunc(10);
	myfunc(std::string("hello"));
	return 0;
}
```
* [classmethod.py](c++/classmethod.py)

input:
------
```python
'''
class methods
'''
class A:
	def __init__(self, x:int, y:int):
		self.x = x
		self.y = y

	@classmethod
	def foo(self):
		print('my classmethod')

	@classmethod
	def bar(self, a:int) ->int:
		return a+1000

def main():
	x = A(1,2)
	x.foo()
	A.foo()
	print x.bar( 100 )
	y = A.bar(200)
	print(y)
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  y;
	int  x;
	A* __init__(int x, int y);
	static void foo();
	static int bar(int a);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
	int A::bar(int a) {

		
		return (a + 1000);
	}
	void A::foo() {

		
		std::cout << std::string("my classmethod") << std::endl;
	}
	A* A::__init__(int x, int y) {

		
		this->x = x;
		this->y = y;
		return this;
	}
int main() {

	
	auto x = std::shared_ptr<A>((new A())->__init__(1, 2)); // new object
	x->foo();
	A::foo();
	std::cout << x->bar(100) << std::endl;
	auto y = A::bar(200);			/* A   */
	std::cout << y << std::endl;
	return 0;
}
```
* [let_styles.py](c++/let_styles.py)

input:
------
```python
'''
let syntax example
'''
NUM = 100

class Foo():
	def __init__(self):
		#let self.data : [NUM]int
		pass

let Foos: []Foo

let TwentyFoos : [20]Foo

mycomp = []int()

def main():
	print Foos

	print len(Foos)
	assert len(Foos) == 0

	f = Foo()
	Foos.push_back(f)
	print len(Foos)
	assert len(Foos)==1

	print len(TwentyFoos)
```
output:
------
```c++

int NUM = 100;
class Foo {
  public:
	std::string __class__;
	bool __initialized__;
	Foo* __init__();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
auto Foos = std::make_shared<std::vector<std::shared_ptr<Foo>>>();
auto TwentyFoos = std::make_shared<std::vector<Foo>>(20);
auto mycomp = ('std::vector<int>*', '{}');
	Foo* Foo::__init__() {

		
		/*pass*/
		return this;
	}
int main() {

	
	std::cout << Foos << std::endl;
	std::cout << Foos->size() << std::endl;
	if (!(( Foos->size() == 0 ))) {throw std::runtime_error("assertion failed: ( Foos->size() == 0 )"); }
	auto f = std::shared_ptr<Foo>((new Foo())->__init__()); // new object
	Foos->push_back(f);
	std::cout << Foos->size() << std::endl;
	if (!(( Foos->size() == 1 ))) {throw std::runtime_error("assertion failed: ( Foos->size() == 1 )"); }
	std::cout << TwentyFoos->size() << std::endl;
	return 0;
}
```
* [listcomp.py](c++/listcomp.py)

input:
------
```python
'''
list comprehension
'''


def main():
	a = []int( x*2 for x in range(10) )
	print(len(a))
	for item in a:
		print(item)

	## TODO fix slice copy:
	## *** Error in `/tmp/listcomp': free(): invalid pointer: 0x000000000216d218 ***
	#b = [][]int( a[:] for i in range(4)	)
	#print(len(b))
	#print(b[0])
	#print(b[1])
	#print(b[2])
	#print(b[3])
```
output:
------
```c++

int main() {

	
	std::vector<int> _comp_a; /*comprehension*/
	for (int x=0; x<10; x++) {
		_comp_a.push_back((x * 2));
	}
	auto a = std::make_shared<std::vector<int>>(_comp_a);
	std::cout << a->size() << std::endl;
	for (auto &item: *a) {
		std::cout << item << std::endl;
	}
	return 0;
}
```
* [while.py](c++/while.py)

input:
------
```python
'''
simple while loops
'''


def main():
	i = 10
	while i > 0:
		i -= 1

	print(i)
```
output:
------
```c++

int main() {

	
	auto i = 10;  /* auto-fallback */
	while (( i > 0 )) {
		i --;
	}
	std::cout << i << std::endl;
	return 0;
}
```
* [globals.py](c++/globals.py)

input:
------
```python
'''
simple globals
'''

class A: pass

let a : A = None
b = 0

def check_globals():
	print('a addr:', a)  ## should not print `0`
	print('b value:', b)

def main():
	global a, b
	check_globals()
	a = A()
	print(a)
	print(a.__class__)
	b = 100
	check_globals()
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<A>  a = nullptr;
int b = 0;
void check_globals() {

	
	std::cout << std::string("a addr:");
std::cout << a;std::cout << std::endl;
	std::cout << std::string("b value:");
std::cout << b;std::cout << std::endl;
}
int main() {

	
	check_globals();
	a = std::shared_ptr<A>(new A());
	std::cout << a << std::endl;
	std::cout << a->__class__ << std::endl;
	b = 100;
	check_globals();
	return 0;
}
```
* [array_of_arrays.py](c++/array_of_arrays.py)

input:
------
```python
'''
array of arrays
'''

def main():
	## variable size vector of vectors,
	## None is allowed as a sub-vector because each sub-vector is wrapped by std::shared_ptr
	arr = [][]int(
		(1,2,3),
		(4,5,6,7,8),
		None,
		#(x*x for x in range(4)),  ## TODO fix listcomps
		(x for x in range(20)),
	)
	print( len(arr))
	print( len(arr[0]) )
	print( len(arr[1]) )
	if arr[2] is None:
		print('nullptr works ok!')
	else:
		print('never reached')

	print('sub 0 items:')
	for i in arr[0]:
		print( i )

	print('sub 1 items:')
	sub = arr[1]
	for i in sub:
		print(i)

	print('sub 3 items:')
	for i in arr[3]:
		print(i)

	print('sub 3 items changed:')
	arr[3][0] = 1000
	arr[3][1] = 1001
	arr[3][2] = 1002
	arr[3][3] = 1003
	for i in arr[3]:
		print(i)
```
output:
------
```c++

int main() {

	
	/* arr = vector of vectors to: int */	
std::vector<int> _r__sub0_arr = {1,2,3};	
std::shared_ptr<std::vector<int>> _sub0_arr = std::make_shared<std::vector<int>>(_r__sub0_arr);	
std::vector<int> _r__sub1_arr = {4,5,6,7,8};	
std::shared_ptr<std::vector<int>> _sub1_arr = std::make_shared<std::vector<int>>(_r__sub1_arr);	
std::vector<int> _comp__subcomp_arr; /*comprehension*/
	for (int x=0; x<20; x++) {
		_comp__subcomp_arr.push_back(x);
	}
	auto _subcomp_arr = std::make_shared<std::vector<int>>(_comp__subcomp_arr);	
std::vector< std::shared_ptr<std::vector<int>> > _ref_arr = {_sub0_arr,_sub1_arr,nullptr,_subcomp_arr};	
std::shared_ptr<std::vector< std::shared_ptr<std::vector<int>> >> arr = std::make_shared<std::vector< std::shared_ptr<std::vector<int>> >>(_ref_arr);
	std::cout << arr->size() << std::endl;
	std::cout << (*arr)[0]->size() << std::endl;
	std::cout << (*arr)[1]->size() << std::endl;
	if (( (*arr)[2] == nullptr )) {
		std::cout << std::string("nullptr works ok!") << std::endl;
	} else {
		std::cout << std::string("never reached") << std::endl;
	}
	std::cout << std::string("sub 0 items:") << std::endl;
	for (auto &i: *(*arr)[0]) {
		std::cout << i << std::endl;
	}
	std::cout << std::string("sub 1 items:") << std::endl;
	auto sub = (*arr)[1];  /* auto-fallback */
	for (auto &i: *sub) {
		std::cout << i << std::endl;
	}
	std::cout << std::string("sub 3 items:") << std::endl;
	for (auto &i: *(*arr)[3]) {
		std::cout << i << std::endl;
	}
	std::cout << std::string("sub 3 items changed:") << std::endl;
	(*(*arr)[3])[0] = 1000;
	(*(*arr)[3])[1] = 1001;
	(*(*arr)[3])[2] = 1002;
	(*(*arr)[3])[3] = 1003;
	for (auto &i: *(*arr)[3]) {
		std::cout << i << std::endl;
	}
	return 0;
	/* arrays:
		arr : int
*/
}
```
* [returns_object.py](c++/returns_object.py)

input:
------
```python
'''
return a class instance
'''
with pointers:
	class A:
		def __init__(self, x:int, y:int):
			self.x = x
			self.y = y

	def create_A() -> A:
		#a = A(1,2)  ## not valid because `a` gets free`ed when function exists
		a = new A(1,2)  ## using `new` the user must manually free the object later
		return a

	def main():
		x = create_A()
		print(x)
		print(x.x)
		print(x.y)
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  y;
	int  x;
	A* __init__(int x, int y);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
A* create_A() {

	
	auto a = (new A)->__init__(1,2);  /* new object */
	return a;
}
	A* A::__init__(int x, int y) {

		
		this->x = x;
		this->y = y;
		return this;
	}
int main() {

	
	auto x = create_A();			/* new variable */
	std::cout << x << std::endl;
	std::cout << x->x << std::endl;
	std::cout << x->y << std::endl;
	return 0;
}
```
* [array_slice_assignment.py](c++/array_slice_assignment.py)

input:
------
```python
'''
array slice assignment syntax
'''

def somefunc():
	a = [1,2,3,4,5]
	assert len(a)==5
	b = [6,7,8,9,10]
	assert len(b)==5
	c = [100, 200]

	print('len a:', len(a))
	#for i in a:
	#	print i

	print 'slice assign front'
	lena = len(a)
	two = 2
	a[:two+1] = b
	print('len a:', len(a))
	assert len(a)==(lena-(two+1))+len(b)
	#assert len(a)==8
	for i in a: print i
	assert a[0]==6
	assert a[5]==4
	assert a[6]==5

	print 'slice assign back'
	b[2:] = c
	for i in b:
		print i
	assert b[0]==6
	assert b[1]==7
	assert b[2]==100
	assert b[3]==200
	print 'slice out of bounds'
	print a
	a[:100] = b
	for v in a:
		print v
	print 'len a:', len(a)

def stackfunc():
	print 'testing stack allocated arrays'
	with stack:
		x = [5]int(1,2,3,4,5)
		assert len(x)==5
		y = [5]int(6,7,8,9,10)
		assert len(y)==5

		z = y[3:]
		assert len(z)==2
		x[3:] = z

		for item in x:
			print item

		assert x[0]==1
		assert x[1]==2
		assert x[2]==3
		assert x[3]==9
		assert x[4]==10

def main():
	somefunc()
	stackfunc()

#main()
```
output:
------
```c++

void somefunc() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
	if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
	std::shared_ptr<std::vector<int>> b( (new std::vector<int>({6,7,8,9,10})) ); /* 1D Array */
	if (!(( b->size() == 5 ))) {throw std::runtime_error("assertion failed: ( b->size() == 5 )"); }
	std::shared_ptr<std::vector<int>> c( (new std::vector<int>({100,200})) ); /* 1D Array */
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	std::cout << std::string("slice assign front") << std::endl;
	auto lena = a->size();			/* new variable */
	auto two = 2;  /* auto-fallback */
	if ((two + 1) >= a->size()) { a->erase(a->begin(), a->end());
} else { a->erase(a->begin(), a->begin()+(two + 1)); }
a->insert(a->begin(), b->begin(), b->end());
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	if (!(( a->size() == ( ((lena - (two + 1)) + b->size()) ) ))) {throw std::runtime_error("assertion failed: ( a->size() == ( ((lena - (two + 1)) + b->size()) ) )"); }
	for (auto &i: (*a)) {
		std::cout << i << std::endl;
	}
	if (!(( (*a)[0] == 6 ))) {throw std::runtime_error("assertion failed: ( (*a)[0] == 6 )"); }
	if (!(( (*a)[5] == 4 ))) {throw std::runtime_error("assertion failed: ( (*a)[5] == 4 )"); }
	if (!(( (*a)[6] == 5 ))) {throw std::runtime_error("assertion failed: ( (*a)[6] == 5 )"); }
	std::cout << std::string("slice assign back") << std::endl;
	b->erase(b->begin()+2, b->end());
b->insert(b->end(), c->begin(), c->end());
	for (auto &i: (*b)) {
		std::cout << i << std::endl;
	}
	if (!(( (*b)[0] == 6 ))) {throw std::runtime_error("assertion failed: ( (*b)[0] == 6 )"); }
	if (!(( (*b)[1] == 7 ))) {throw std::runtime_error("assertion failed: ( (*b)[1] == 7 )"); }
	if (!(( (*b)[2] == 100 ))) {throw std::runtime_error("assertion failed: ( (*b)[2] == 100 )"); }
	if (!(( (*b)[3] == 200 ))) {throw std::runtime_error("assertion failed: ( (*b)[3] == 200 )"); }
	std::cout << std::string("slice out of bounds") << std::endl;
	std::cout << a << std::endl;
	if (100 >= a->size()) { a->erase(a->begin(), a->end());
} else { a->erase(a->begin(), a->begin()+100); }
a->insert(a->begin(), b->begin(), b->end());
	for (auto &v: (*a)) {
		std::cout << v << std::endl;
	}
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	/* arrays:
		a : int
		c : int
		b : int
*/
}
void stackfunc() {

	
	std::cout << std::string("testing stack allocated arrays") << std::endl;
		int x[5] = {1,2,3,4,5};
	if (!(( 5 == 5 ))) {throw std::runtime_error("assertion failed: ( 5 == 5 )"); }
	int y[5] = {6,7,8,9,10};
	if (!(( 5 == 5 ))) {throw std::runtime_error("assertion failed: ( 5 == 5 )"); }
	/* <fixed size slice> 3 : None : None */
	int z[2] = {y[3],y[4]};
	if (!(( 2 == 2 ))) {throw std::runtime_error("assertion failed: ( 2 == 2 )"); }
		int __L = 0;
	for (int __i=3; __i<5; __i++) {
	  x[__i] = z[__L];
	  __L ++;
	}
	for (int __idx=0; __idx<5; __idx++) {
	int item = x[__idx];
		std::cout << item << std::endl;
	}
	if (!(( x[0] == 1 ))) {throw std::runtime_error("assertion failed: ( x[0] == 1 )"); }
	if (!(( x[1] == 2 ))) {throw std::runtime_error("assertion failed: ( x[1] == 2 )"); }
	if (!(( x[2] == 3 ))) {throw std::runtime_error("assertion failed: ( x[2] == 3 )"); }
	if (!(( x[3] == 9 ))) {throw std::runtime_error("assertion failed: ( x[3] == 9 )"); }
	if (!(( x[4] == 10 ))) {throw std::runtime_error("assertion failed: ( x[4] == 10 )"); }
	/* arrays:
		y : ('int', '5')
		x : ('int', '5')
		z : ('int', '2')
*/
}
int main() {

	
	somefunc();
	stackfunc();
	return 0;
}
```
* [cyclic.py](c++/cyclic.py)

input:
------
```python
'''
detect cyclic parent/child, and insert weakref
'''
class Parent:
	def __init__(self, y:int, children:[]Child ):
		self.children = children
		self.y = y

	def create_child(self, x:int, parent:Parent) ->Child:
		child = Child(x, parent)
		self.children.push_back( child )
		return child

	def say(self, msg:string):
		print(msg)

class Child:
	def __init__(self, x:int, parent:Parent ):
		self.x = x
		self.parent = parent

	def foo(self) ->int:
		'''
		It is also valid to use `par=self.parent`,
		but it is more clear to use `weakref.unwrap(self.parent)`
		'''
		par = weak.unwrap(self.parent)
		if par is not None:
			return self.x * par.y
		else:
			print('parent is gone..')

	def bar(self):
		'''
		below `self.parent` is directly used in expressions,
		and not first assigned to a variable.
		for each use of self.parent the weakref will be promoted
		to a shared pointer, and then fall out of scope, 
		which is slower than above.
		'''
		self.parent.say('hello parent')
		print(self.parent.y)


def main():
	#children = []Child(None,None)
	children = []Child()
	p = Parent( 1000, children )
	print 'parent:', p

	c1 = p.create_child(1, p)
	c2 = p.create_child(2, p)
	c3 = p.create_child(3, p)
	print 'children:'
	print c1
	print c2
	print c3
```
output:
------
```c++

class Parent {
  public:
	std::string __class__;
	bool __initialized__;
	int  y;
	std::shared_ptr<std::vector<std::shared_ptr<Child>>>  children;
	Parent* __init__(int y, std::shared_ptr<std::vector<std::shared_ptr<Child>>> children);
	std::shared_ptr<Child> create_child(int x, std::shared_ptr<Parent> parent);
	void say(std::string msg);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Parent() {__class__ = std::string("Parent"); __initialized__ = true;}
	Parent(bool init) {__class__ = std::string("Parent"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class Child {
  public:
	std::string __class__;
	bool __initialized__;
	int  x;
	std::weak_ptr<Parent>  parent;
	Child* __init__(int x, std::shared_ptr<Parent> parent);
	int foo();
	void bar();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Child() {__class__ = std::string("Child"); __initialized__ = true;}
	Child(bool init) {__class__ = std::string("Child"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
/**
 * 
 * 		below `self.parent` is directly used in expressions,
 * 		and not first assigned to a variable.
 * 		for each use of self.parent the weakref will be promoted
 * 		to a shared pointer, and then fall out of scope, 
 * 		which is slower than above.
 * 		
 */
	void Child::bar() {

		
		std::string("\n		below `self.parent` is directly used in expressions,\n		and not first assigned to a variable.\n		for each use of self.parent the weakref will be promoted\n		to a shared pointer, and then fall out of scope, \n		which is slower than above.\n		");
		this->parent.lock()->say(std::string("hello parent"));
		std::cout << this->parent.lock()->y << std::endl;
	}
/**
 * 
 * 		It is also valid to use `par=self.parent`,
 * 		but it is more clear to use `weakref.unwrap(self.parent)`
 * 		
 */
	int Child::foo() {

		
		std::string("\n		It is also valid to use `par=self.parent`,\n		but it is more clear to use `weakref.unwrap(self.parent)`\n		");
		auto par = this->parent.lock();			/* weak   */
		if (( par != nullptr )) {
			return (this->x * par->y);
		} else {
			std::cout << std::string("parent is gone..") << std::endl;
		}
	}
	Child* Child::__init__(int x, std::shared_ptr<Parent> parent) {

		
		this->x = x;
		this->parent = parent;
		return this;
	}
	void Parent::say(std::string msg) {

		
		std::cout << msg << std::endl;
	}
	std::shared_ptr<Child> Parent::create_child(int x, std::shared_ptr<Parent> parent) {

		
		auto child = std::shared_ptr<Child>((new Child())->__init__(x, parent)); // new object
		this->children->push_back(child);
		return child;
	}
	Parent* Parent::__init__(int y, std::shared_ptr<std::vector<std::shared_ptr<Child>>> children) {

		
		this->children = children;
		this->y = y;
		return this;
		/* arrays:
			children : []Child
*/
	}
int main() {

	
	std::shared_ptr<std::vector<std::shared_ptr<Child>>> children( ( new std::vector<std::shared_ptr<Child>>({}) ) ); /* 1D Array */
	auto p = std::shared_ptr<Parent>((new Parent())->__init__(1000, children)); // new object
	std::cout << std::string("parent:");
std::cout << p;std::cout << std::endl;
	auto c1 = p->create_child(1, p);			/* p   */
	auto c2 = p->create_child(2, p);			/* p   */
	auto c3 = p->create_child(3, p);			/* p   */
	std::cout << std::string("children:") << std::endl;
	std::cout << c1 << std::endl;
	std::cout << c2 << std::endl;
	std::cout << c3 << std::endl;
	return 0;
	/* arrays:
		children : Child
*/
}
```
* [array_methods.py](c++/array_methods.py)

input:
------
```python
'''
array methods: append, pop, etc.
'''

def somefunc():
	a = []int(1,2,3,4,5)
	print('len a:', len(a))
	assert len(a)==5
	b = a.pop()
	print('len a after pop:', len(a))
	assert len(a)==4
	assert b==5

	#b = a[len(a)-1]
	a.pop()
	print('len a:', len(a))
	assert len(a)==3
	print(b)
	a.insert(0, 1000)
	#a.insert(a.begin(), 1000)

	print('len a:', len(a))
	print(a[0])
	assert a[0]==1000
	assert len(a)==4

	c = a.pop(0)
	assert c==1000
	assert len(a)==3
	print 'testing insert empty array'
	empty = []int(10,20)
	#a.insert(1, empty.begin(), empty.end() ) ## TODO?
	a.insert( a.begin()+1, empty.begin(), empty.end() )
	for val in a:
		print val

	#error: invalid use of void expression a->insert(a->begin()+0, a->pop_back());
	#a.insert(0, a.pop())  ## TODO fixme

def stackfunc():
	with stack:
		arr = [5]int(1,2,3,4,5)
		print('sizeof arr:', sizeof(arr))  ## says 20 bytes?
		#val = a.pop()  ## not possible for stack allocated fixed size arrays

		## pop and insert is allowed because the array remains the same size
		## this generates a for loop that moves all elements past the insertion
		## index forward by one index.
		arr.insert(0, arr.pop())
		assert arr[0]==5
		assert arr[1]==1
		assert arr[4]==4

		arr2 = [5]int(1,2,3,4,5)

		copy = arr2[:]
		assert len(copy)==5


		reversed = arr2[::-1]
		assert len(reversed)==len(arr2)
		assert reversed[0]==5
		assert reversed[1]==4
		assert reversed[2]==3
		assert reversed[3]==2
		assert reversed[4]==1
		print 'slice front and reverse'
		k = 2
		s = arr2[k::-1]
		for val in s:
			print val
		assert s[0]==5
		assert s[1]==4
		assert s[2]==3

		print 'testing insert/pop on stack array'
		arr3 = [4]int(1,2,3,4)
		#arr3.insert(k, arr.pop(0))  ## not allowed
		arr3.insert(k, arr3.pop(0))
		for val in arr3:
			print val

		assert arr3[0]==2
		assert arr3[1]==3
		assert arr3[2]==1
		assert arr3[3]==4

def main():
	somefunc()
	stackfunc()
	print('OK')

```
output:
------
```c++

void somefunc() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
	auto b = (*a)[ a->size()-1 ];
a->pop_back();
	std::cout << std::string("len a after pop:");
std::cout << a->size();std::cout << std::endl;
	if (!(( a->size() == 4 ))) {throw std::runtime_error("assertion failed: ( a->size() == 4 )"); }
	if (!(( b == 5 ))) {throw std::runtime_error("assertion failed: ( b == 5 )"); }
	a->pop_back();
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	if (!(( a->size() == 3 ))) {throw std::runtime_error("assertion failed: ( a->size() == 3 )"); }
	std::cout << b << std::endl;
	a->insert(a->begin()+0, 1000);
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	std::cout << (*a)[0] << std::endl;
	if (!(( (*a)[0] == 1000 ))) {throw std::runtime_error("assertion failed: ( (*a)[0] == 1000 )"); }
	if (!(( a->size() == 4 ))) {throw std::runtime_error("assertion failed: ( a->size() == 4 )"); }
	auto c = (*a)[0];
a->erase(a->begin(),a->begin()+1);
	if (!(( c == 1000 ))) {throw std::runtime_error("assertion failed: ( c == 1000 )"); }
	if (!(( a->size() == 3 ))) {throw std::runtime_error("assertion failed: ( a->size() == 3 )"); }
	std::cout << std::string("testing insert empty array") << std::endl;
	std::shared_ptr<std::vector<int>> empty( (new std::vector<int>({10,20})) ); /* 1D Array */
	a->insert((a->begin() + 1), empty->begin(), empty->end());
	for (auto &val: (*a)) {
		std::cout << val << std::endl;
	}
	/* arrays:
		a : int
		empty : int
*/
}
void stackfunc() {

	
		int arr[5] = {1,2,3,4,5};
	std::cout << std::string("sizeof arr:");
std::cout << sizeof(arr);std::cout << std::endl;
	auto __back__ = arr[5-1];
	for (int __i=5-1; __i>0; __i--) {
	  arr[__i] = arr[__i-1];
	}
	arr[0] = __back__;
	if (!(( arr[0] == 5 ))) {throw std::runtime_error("assertion failed: ( arr[0] == 5 )"); }
	if (!(( arr[1] == 1 ))) {throw std::runtime_error("assertion failed: ( arr[1] == 1 )"); }
	if (!(( arr[4] == 4 ))) {throw std::runtime_error("assertion failed: ( arr[4] == 4 )"); }
	int arr2[5] = {1,2,3,4,5};
	/* <fixed size slice> None : None : None */
	int copy[5] = {arr2[0],arr2[1],arr2[2],arr2[3],arr2[4]};
	if (!(( 5 == 5 ))) {throw std::runtime_error("assertion failed: ( 5 == 5 )"); }
	/* <fixed size slice> None : None : -1 */
	int reversed[5] = {arr2[4],arr2[3],arr2[2],arr2[1],arr2[0]};
	if (!(( 5 == 5 ))) {throw std::runtime_error("assertion failed: ( 5 == 5 )"); }
	if (!(( reversed[0] == 5 ))) {throw std::runtime_error("assertion failed: ( reversed[0] == 5 )"); }
	if (!(( reversed[1] == 4 ))) {throw std::runtime_error("assertion failed: ( reversed[1] == 4 )"); }
	if (!(( reversed[2] == 3 ))) {throw std::runtime_error("assertion failed: ( reversed[2] == 3 )"); }
	if (!(( reversed[3] == 2 ))) {throw std::runtime_error("assertion failed: ( reversed[3] == 2 )"); }
	if (!(( reversed[4] == 1 ))) {throw std::runtime_error("assertion failed: ( reversed[4] == 1 )"); }
	std::cout << std::string("slice front and reverse") << std::endl;
	auto k = 2;  /* auto-fallback */
	/* <fixed size slice> k : None : -1 */
	int s[5-k];
	int __L = 0;
	for (int __i=5-1; __i>=k; __i--) {
	  s[__L] = arr2[__i];
	  __L ++;
	}
	for (int __idx=0; __idx<5-k; __idx++) {
	int val = s[__idx];
		std::cout << val << std::endl;
	}
	if (!(( s[0] == 5 ))) {throw std::runtime_error("assertion failed: ( s[0] == 5 )"); }
	if (!(( s[1] == 4 ))) {throw std::runtime_error("assertion failed: ( s[1] == 4 )"); }
	if (!(( s[2] == 3 ))) {throw std::runtime_error("assertion failed: ( s[2] == 3 )"); }
	std::cout << std::string("testing insert/pop on stack array") << std::endl;
	int arr3[4] = {1,2,3,4};
	auto __front__ = arr3[0];
	for (int __i=1; __i<=k; __i++) {
	  arr3[__i-1] = arr3[__i];
	}
	arr3[k] = __front__;
	for (int __idx=0; __idx<4; __idx++) {
	int val = arr3[__idx];
		std::cout << val << std::endl;
	}
	if (!(( arr3[0] == 2 ))) {throw std::runtime_error("assertion failed: ( arr3[0] == 2 )"); }
	if (!(( arr3[1] == 3 ))) {throw std::runtime_error("assertion failed: ( arr3[1] == 3 )"); }
	if (!(( arr3[2] == 1 ))) {throw std::runtime_error("assertion failed: ( arr3[2] == 1 )"); }
	if (!(( arr3[3] == 4 ))) {throw std::runtime_error("assertion failed: ( arr3[3] == 4 )"); }
	/* arrays:
		arr : ('int', '5')
		reversed : ('int', '5')
		s : ('int', '5-k')
		arr3 : ('int', '4')
		arr2 : ('int', '5')
		copy : ('int', '5')
*/
}
int main() {

	
	somefunc();
	stackfunc();
	std::cout << std::string("OK") << std::endl;
	return 0;
}
```
* [generics_array_subclasses.py](c++/generics_array_subclasses.py)

input:
------
```python
'''
generics classes with common base.
'''
class A:
	def __init__(self, x:int):
		self.x = x

	def method1(self) -> int:
		return self.x
	def getname(self) -> string:
		return self.__class__

class B(A):
	def method1(self) ->int:
		return self.x * 2
	def method2(self, y:int):
		print( self.x + y )

class C(A):
	def method1(self) ->int:
		return self.x + 200

	def say_hi(self):
		print('hi from C')


def my_generic( g:A ) ->int:
	return g.method1()


def main():
	a = A( 1 )
	b = B( 200 )
	c = C( 3000 )

	print(a.__class__)
	print(b.__class__)
	print(c.__class__)
	print('- - - - - - -')

	arr = []A( a,b,c )
	for item in arr:
		## just prints 100's because c++ runtime method dispatcher thinks item
		## is of class type `A`
		print(item.__class__)
		print( my_generic(item) )

	print('- - - - - - -')

	for item in arr:
		print(item.getname())
		print(item.x)

		## to get to the real subclasses, we need if-isinstance
		if isinstance(item, B):
			print('item is B')
			item.method2( 20 )

		if isinstance(item, C):
			print('item is C')
			item.say_hi()

```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  x;
	A* __init__(int x);
	int method1();
	std::string getname();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x']
	int method1();
	void method2(int y);
	B* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x']
	int method1();
	void say_hi();
	C* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
int my_generic(std::shared_ptr<A> g) {

	
	return g->method1();
}
	C* C::__init__(int x) {

		
		this->x = x;
		return this;
	}
	void C::say_hi() {

		
		std::cout << std::string("hi from C") << std::endl;
	}
	int C::method1() {

		
		return (this->x + 200);
	}
	B* B::__init__(int x) {

		
		this->x = x;
		return this;
	}
	void B::method2(int y) {

		
		std::cout << (this->x + y) << std::endl;
	}
	int B::method1() {

		
		return (this->x * 2);
	}
	std::string A::getname() {

		
		return this->__class__;
	}
	int A::method1() {

		
		return this->x;
	}
	A* A::__init__(int x) {

		
		this->x = x;
		return this;
	}
int main() {

	
	auto a = std::shared_ptr<A>((new A())->__init__(1)); // new object
	auto b = std::shared_ptr<B>((new B())->__init__(200)); // new object
	auto c = std::shared_ptr<C>((new C())->__init__(3000)); // new object
	std::cout << a->__class__ << std::endl;
	std::cout << b->__class__ << std::endl;
	std::cout << c->__class__ << std::endl;
	std::cout << std::string("- - - - - - -") << std::endl;
	std::shared_ptr<std::vector<std::shared_ptr<A>>> arr( ( new std::vector<std::shared_ptr<A>>({a,b,c}) ) ); /* 1D Array */
	for (auto &item: (*arr)) {
		std::cout << item->__class__ << std::endl;
		std::cout << my_generic(item) << std::endl;
	}
	std::cout << std::string("- - - - - - -") << std::endl;
	for (auto &item: (*arr)) {
		std::cout << item->getname() << std::endl;
		std::cout << item->x << std::endl;
		if ((item->__class__==std::string("B"))) {
			auto _cast_item = std::static_pointer_cast<B>(item);
			std::cout << std::string("item is B") << std::endl;
			_cast_item->method2(20);
		}
		if ((item->__class__==std::string("C"))) {
			auto _cast_item = std::static_pointer_cast<C>(item);
			std::cout << std::string("item is C") << std::endl;
			_cast_item->say_hi();
		}
	}
	return 0;
	/* arrays:
		arr : A
*/
}
```
* [subscript.py](c++/subscript.py)

input:
------
```python
'''
simple subscript
'''


def main():
	a = []int(1,2,3)
	index = 0
	a[ index ] = 100
	print(a[index])

	s = "hello world"
	print(s)
	print(s[0])
	print(s[1])
	print(s[2])
	print(s[3])
	if s[0]=='h':
		print('ok')
	else:
		print('error')
```
output:
------
```c++

int main() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3})) ); /* 1D Array */
	auto index = 0;  /* auto-fallback */
	(*a)[index] = 100;
	std::cout << (*a)[index] << std::endl;
	auto s = std::string("hello world");  /* auto-fallback */
	std::cout << s << std::endl;
	std::cout << s.substr(0,1) << std::endl;
	std::cout << s.substr(1,1) << std::endl;
	std::cout << s.substr(2,1) << std::endl;
	std::cout << s.substr(3,1) << std::endl;
	if (( s.substr(0,1) == std::string("h") )) {
		std::cout << std::string("ok") << std::endl;
	} else {
		std::cout << std::string("error") << std::endl;
	}
	return 0;
	/* arrays:
		a : int
*/
}
```
* [returns_subclasses.py](c++/returns_subclasses.py)

input:
------
```python
'''
returns subclasses
'''
class A:
	def __init__(self, x:int):
		self.x = x
	def method(self) -> int:
		return self.x

class B(A):
	def foo(self) ->int:
		return self.x * 2

class C(A):
	def bar(self) ->int:
		return self.x + 200

class D(C):
	def hey(self) ->int:
		return self.x + 1


def some_subclass( x:int ) ->A:
	switch x:
		case 0:
			a = A(1)
			return a
		case 1:
			b = B(2)
			return b
		case 2:
			c = C(3)
			return c
		case 3:
			d = D(4)
			return d


def main():
	a = some_subclass(0)
	b = some_subclass(1)
	c = some_subclass(2)
	d = some_subclass(3)

	print(a.getclassname())
	print(b.getclassname())
	print(c.getclassname())
	print(d.getclassname())

	print(a.method())
	print a.x
	print(b.method())
	print b.x
	print(c.method())
	print c.x
	print(d.method())
	print d.x

	print('- - - - - - - ')
	if isinstance(b, B):
		print('b is type B')
		print(b.method())
		print(b.foo())
	else:
		print('error: b is not type B')

	if isinstance(c, C):
		print('c is type C')
		print(c.method())
		print(c.bar())
	else:
		print('error: c is not type C')

	if isinstance(d, D):
		print('d is type D')
		#print(d.bar())  ## TODO, subclass from C.
		print(d.hey())
	else:
		print('error: d is not type D')

	print('------------------')
	for i in range(3):
		o = some_subclass(i)
		print(o.method())
		if isinstance(o, B):
			print(o.foo())
		if isinstance(o,C):		## TODO-FIX elif isinstance(o,C)
			print(o.bar())

	print('end of test')
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  x;
	A* __init__(int x);
	int method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x']
	int foo();
	B* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x']
	int bar();
	C* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class D:  public C {
  public:
//	members from class: A  ['x']
	int hey();
	D* __init__(int x);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	D() {__class__ = std::string("D"); __initialized__ = true;}
	D(bool init) {__class__ = std::string("D"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<A> some_subclass(int x) {

	
		switch (x) {
		case 0: {
	auto a = std::shared_ptr<A>((new A())->__init__(1)); // new object
	return a;
	} break;
		case 1: {
	auto b = std::shared_ptr<B>((new B())->__init__(2)); // new object
	return b;
	} break;
		case 2: {
	auto c = std::shared_ptr<C>((new C())->__init__(3)); // new object
	return c;
	} break;
		case 3: {
	auto d = std::shared_ptr<D>((new D())->__init__(4)); // new object
	return d;
	} break;
	}
}
	D* D::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int D::hey() {

		
		return (this->x + 1);
	}
	C* C::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int C::bar() {

		
		return (this->x + 200);
	}
	B* B::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int B::foo() {

		
		return (this->x * 2);
	}
	int A::method() {

		
		return this->x;
	}
	A* A::__init__(int x) {

		
		this->x = x;
		return this;
	}
int main() {

	
	auto a = some_subclass(0);			/* new variable */
	auto b = some_subclass(1);			/* new variable */
	auto c = some_subclass(2);			/* new variable */
	auto d = some_subclass(3);			/* new variable */
	std::cout << a->getclassname() << std::endl;
	std::cout << b->getclassname() << std::endl;
	std::cout << c->getclassname() << std::endl;
	std::cout << d->getclassname() << std::endl;
	std::cout << a->method() << std::endl;
	std::cout << a->x << std::endl;
	std::cout << b->method() << std::endl;
	std::cout << b->x << std::endl;
	std::cout << c->method() << std::endl;
	std::cout << c->x << std::endl;
	std::cout << d->method() << std::endl;
	std::cout << d->x << std::endl;
	std::cout << std::string("- - - - - - - ") << std::endl;
	if ((b->__class__==std::string("B"))) {
		auto _cast_b = std::static_pointer_cast<B>(b);
		std::cout << std::string("b is type B") << std::endl;
		std::cout << _cast_b->method() << std::endl;
		std::cout << _cast_b->foo() << std::endl;
	} else {
		std::cout << std::string("error: b is not type B") << std::endl;
	}
	if ((c->__class__==std::string("C"))) {
		auto _cast_c = std::static_pointer_cast<C>(c);
		std::cout << std::string("c is type C") << std::endl;
		std::cout << _cast_c->method() << std::endl;
		std::cout << _cast_c->bar() << std::endl;
	} else {
		std::cout << std::string("error: c is not type C") << std::endl;
	}
	if ((d->__class__==std::string("D"))) {
		auto _cast_d = std::static_pointer_cast<D>(d);
		std::cout << std::string("d is type D") << std::endl;
		std::cout << _cast_d->hey() << std::endl;
	} else {
		std::cout << std::string("error: d is not type D") << std::endl;
	}
	std::cout << std::string("------------------") << std::endl;
	for (int i=0; i<3; i++) {
		auto o = some_subclass(i);			/* new variable */
		std::cout << o->method() << std::endl;
		if ((o->__class__==std::string("B"))) {
			auto _cast_o = std::static_pointer_cast<B>(o);
			std::cout << _cast_o->foo() << std::endl;
		}
		if ((o->__class__==std::string("C"))) {
			auto _cast_o = std::static_pointer_cast<C>(o);
			std::cout << _cast_o->bar() << std::endl;
		}
	}
	std::cout << std::string("end of test") << std::endl;
	return 0;
}
```
* [free_memory.py](c++/free_memory.py)

input:
------
```python
'''
delete pointer
'''
class A:
	def __init__(self, x:int ):
		self.x = x
	def __del__(self):
		print( 'goodbye')

def main():
	a = A(1)
	print a
	del a
	print 'done'
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  x;
	A* __init__(int x);
	~A();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
	A::~A() {

		
		std::cout << std::string("goodbye") << std::endl;
	}
	A* A::__init__(int x) {

		
		this->x = x;
		return this;
	}
int main() {

	
	auto a = std::shared_ptr<A>((new A())->__init__(1)); // new object
	std::cout << a << std::endl;
	a.reset();
	std::cout << std::string("done") << std::endl;
	return 0;
}
```
* [if_none.py](c++/if_none.py)

input:
------
```python
'''
if a is None
'''

with stack:
	class A:
		def __init__(self):
			print 'new class A'
		def is_initialized(self) -> bool:
			return self.__initialized__

	def test():
		a = A()
		print a.is_initialized()
		assert a.is_initialized()
		if a is not None:
			print 'a can be checked if not None'

		let b:A = None
		print b.is_initialized()
		if b is None:
			print 'b is acting like a nullptr'

		assert b.is_initialized() is False

def main():
	test()
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	A __init__();
	bool is_initialized();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return __class__;}
};
void test() {

	
	auto a = A().__init__(); // new object
	std::cout << a.is_initialized() << std::endl;
	if (!(a.is_initialized())) {throw std::runtime_error("assertion failed: a.is_initialized()"); }
	if (( a != nullptr )) {
		std::cout << std::string("a can be checked if not None") << std::endl;
	}
	A  b = A(false);
	std::cout << b.is_initialized() << std::endl;
	if (( b == nullptr )) {
		std::cout << std::string("b is acting like a nullptr") << std::endl;
	}
	if (!(( b.is_initialized() == false ))) {throw std::runtime_error("assertion failed: ( b.is_initialized() == false )"); }
}
	bool A::is_initialized() {

		
		return (*this).__initialized__;
	}
	A A::__init__() {

		
		std::cout << std::string("new class A") << std::endl;
		return *this;
	}
int main() {

	
	test();
	return 0;
}
```
* [array_of_arrays_objects.py](c++/array_of_arrays_objects.py)

input:
------
```python
'''
array of arrays objects
'''

class A:
	def __init__(self, id:int):
		self.id = id

	def method(self):
		print(self.id)

def main():
	a1 = A(1)
	a2 = A(2)
	a3 = A(3)

	arr = [][]A(
		(a1,a2,a3, A(4)),
		(a1,None),
		None,
	)
	print('length of array: ', len(arr))
	print( 'len subarray 0:  ', len(arr[0]) )
	print( 'len subarray 1:  ', len(arr[1]) )
	print('subarray 2 is nullptr:  ',arr[2] )
	print('subarray 0 ptr addr: ', arr[0])

	arr[0][2].method()
```
output:
------
```c++

class A {
  public:
	std::string __class__;
	bool __initialized__;
	int  id;
	A* __init__(int id);
	void method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
	void A::method() {

		
		std::cout << this->id << std::endl;
	}
	A* A::__init__(int id) {

		
		this->id = id;
		return this;
	}
int main() {

	
	auto a1 = std::shared_ptr<A>((new A())->__init__(1)); // new object
	auto a2 = std::shared_ptr<A>((new A())->__init__(2)); // new object
	auto a3 = std::shared_ptr<A>((new A())->__init__(3)); // new object
	/* arr = vector of vectors to: A */	
std::vector<  std::shared_ptr<A>  > _r__sub0_arr = {a1,a2,a3,std::shared_ptr<A>((new A())->__init__(4))};	
std::shared_ptr<std::vector<  std::shared_ptr<A>  >> _sub0_arr = std::make_shared<std::vector<  std::shared_ptr<A>  >>(_r__sub0_arr);	
std::vector<  std::shared_ptr<A>  > _r__sub1_arr = {a1,nullptr};	
std::shared_ptr<std::vector<  std::shared_ptr<A>  >> _sub1_arr = std::make_shared<std::vector<  std::shared_ptr<A>  >>(_r__sub1_arr);	
std::vector< std::shared_ptr<std::vector<  std::shared_ptr<A>  >> > _ref_arr = {_sub0_arr,_sub1_arr,nullptr};	
std::shared_ptr<std::vector< std::shared_ptr<std::vector<  std::shared_ptr<A>  >> >> arr = std::make_shared<std::vector< std::shared_ptr<std::vector<  std::shared_ptr<A>  >> >>(_ref_arr);
	std::cout << std::string("length of array: ");
std::cout << arr->size();std::cout << std::endl;
	std::cout << std::string("len subarray 0:  ");
std::cout << (*arr)[0]->size();std::cout << std::endl;
	std::cout << std::string("len subarray 1:  ");
std::cout << (*arr)[1]->size();std::cout << std::endl;
	std::cout << std::string("subarray 2 is nullptr:  ");
std::cout << (*arr)[2];std::cout << std::endl;
	std::cout << std::string("subarray 0 ptr addr: ");
std::cout << (*arr)[0];std::cout << std::endl;
	(*(*arr)[0])[2]->method();
	return 0;
	/* arrays:
		arr : A
*/
}
```
* [cyclic_simple.py](c++/cyclic_simple.py)

input:
------
```python
'''
detect cyclic parent/child, and insert weakref
'''
class Parent:
	def __init__(self, children:[]Child ):
		self.children = children

class Child:
	def __init__(self, parent:Parent ):
		self.parent = parent

	def foo(self) ->int:
		par = self.parent
		if par is not None:
			return 1
		else:
			print('parent is gone..')

	def bar(self):
		print self.parent.children

def make_child(p:Parent) -> Child:
	c = Child(p)
	p.children.push_back(c)
	return c


def main():
	children = []Child()
	p = Parent( children )
	c1 = make_child(p)
	c2 = make_child(p)
	print c1.foo()
	c1.bar()
	del p
	print c1.foo()
	#uncomment to segfault##c1.bar()
```
output:
------
```c++

class Parent {
  public:
	std::string __class__;
	bool __initialized__;
	std::shared_ptr<std::vector<std::shared_ptr<Child>>>  children;
	Parent* __init__(std::shared_ptr<std::vector<std::shared_ptr<Child>>> children);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Parent() {__class__ = std::string("Parent"); __initialized__ = true;}
	Parent(bool init) {__class__ = std::string("Parent"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
class Child {
  public:
	std::string __class__;
	bool __initialized__;
	std::weak_ptr<Parent>  parent;
	Child* __init__(std::shared_ptr<Parent> parent);
	int foo();
	void bar();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Child() {__class__ = std::string("Child"); __initialized__ = true;}
	Child(bool init) {__class__ = std::string("Child"); __initialized__ = init;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<Child> make_child(std::shared_ptr<Parent> p) {

	
	auto c = std::shared_ptr<Child>((new Child())->__init__(p)); // new object
	p->children->push_back(c);
	return c;
}
	void Child::bar() {

		
		std::cout << this->parent.lock()->children << std::endl;
	}
	int Child::foo() {

		
		auto par = this->parent.lock();  /* auto-fallback */
		if (( par != nullptr )) {
			return 1;
		} else {
			std::cout << std::string("parent is gone..") << std::endl;
		}
	}
	Child* Child::__init__(std::shared_ptr<Parent> parent) {

		
		this->parent = parent;
		return this;
	}
	Parent* Parent::__init__(std::shared_ptr<std::vector<std::shared_ptr<Child>>> children) {

		
		this->children = children;
		return this;
		/* arrays:
			children : []Child
*/
	}
int main() {

	
	std::shared_ptr<std::vector<std::shared_ptr<Child>>> children( ( new std::vector<std::shared_ptr<Child>>({}) ) ); /* 1D Array */
	auto p = std::shared_ptr<Parent>((new Parent())->__init__(children)); // new object
	auto c1 = make_child(p);			/* new variable */
	auto c2 = make_child(p);			/* new variable */
	std::cout << c1->foo() << std::endl;
	c1->bar();
	p.reset();
	std::cout << c1->foo() << std::endl;
	return 0;
	/* arrays:
		children : Child
*/
}
```
* [returns_array2D.py](c++/returns_array2D.py)

input:
------
```python
'''
returns array of arrays
'''
def make_array() -> [][]int:
	arr = [][]int(
		(1,2,3),
		(4,5,6,7,8)
	)
	return arr

def test_array( arr:[][]int ):
	print( arr[0][0] )

def main():
	a = make_array()
	print( len(a))
	print( len(a[0]) )
	print( len(a[1]) )

	test_array(a)
```
output:
------
```c++

std::shared_ptr<std::vector<std::shared_ptr<std::vector<int>>>> make_array() {

	
	/* arr = vector of vectors to: int */	
std::vector<int> _r__sub0_arr = {1,2,3};	
std::shared_ptr<std::vector<int>> _sub0_arr = std::make_shared<std::vector<int>>(_r__sub0_arr);	
std::vector<int> _r__sub1_arr = {4,5,6,7,8};	
std::shared_ptr<std::vector<int>> _sub1_arr = std::make_shared<std::vector<int>>(_r__sub1_arr);	
std::vector< std::shared_ptr<std::vector<int>> > _ref_arr = {_sub0_arr,_sub1_arr};	
std::shared_ptr<std::vector< std::shared_ptr<std::vector<int>> >> arr = std::make_shared<std::vector< std::shared_ptr<std::vector<int>> >>(_ref_arr);
	return arr;
	/* arrays:
		arr : int
*/
}
void test_array(std::shared_ptr<std::vector<std::shared_ptr<std::vector<int>>>> arr) {

	
	std::cout << (*(*arr)[0])[0] << std::endl;
	/* arrays:
		arr : [][]int
*/
}
int main() {

	
	auto a = make_array();			/* new variable */
	std::cout << a->size() << std::endl;
	std::cout << (*a)[0]->size() << std::endl;
	std::cout << (*a)[1]->size() << std::endl;
	test_array(a);
	return 0;
}
```
* [try_except_finally.py](c++/try_except_finally.py)

input:
------
```python
'''
c++ finally
'''

def myfunc():

	a = False
	try:
		raise RuntimeError('oops')
	except RuntimeError:
		print 'caught RuntimeError OK'
		a = True

	assert a == True


	c = False
	try:
		raise IOError('my ioerror')

	except IOError as err:
		print 'caught my ioerr'
		print err.what()
		#raise err  ## rethrow works ok
		c = True
	assert c == True


	b = False

	try:
		print('trying something that will fail...')
		print('some call that fails at runtime')
		f = open('/tmp/nosuchfile')
	except RuntimeError:
		print 'this should not happen'
	except IOError:
		print 'CAUGHT IOError OK'
		## it is ok to raise or return in the except block,
		## the finally block will be run before any of this happens
		#raise RuntimeError('rethrowing error')  ## this works
		return

	except:
		print('CAUGHT UNKNOWN EXECEPTION')
		## raise another exception
		raise RuntimeError('got unknown exception')
	finally:
		print('FINALLY')
		b = True

	assert b == True





def main():
	myfunc()
```
output:
------
```c++

void myfunc() {

	
	auto a = false;  /* auto-fallback */
	try {
		throw RuntimeError(std::string("oops"));
	}
	catch (std::runtime_error* __error__) {
		std::string __errorname__ = __parse_error_type__(__error__);
		if (__errorname__ == std::string("RuntimeError")) {
			std::cout << std::string("caught RuntimeError OK") << std::endl;
			a = true;
		}
	}
	if (!(( a == true ))) {throw std::runtime_error("assertion failed: ( a == true )"); }
	auto c = false;  /* auto-fallback */
	try {
		throw IOError(std::string("my ioerror"));
	}
	catch (std::runtime_error* __error__) {
		std::string __errorname__ = __parse_error_type__(__error__);
		if (__errorname__ == std::string("IOError")) {
			auto err = __error__;
			std::cout << std::string("caught my ioerr") << std::endl;
			std::cout << err->what() << std::endl;
			c = true;
		}
	}
	if (!(( c == true ))) {throw std::runtime_error("assertion failed: ( c == true )"); }
	auto b = false;  /* auto-fallback */
	bool __finally_done_1 = false;
	try {
		std::cout << std::string("trying something that will fail...") << std::endl;
		std::cout << std::string("some call that fails at runtime") << std::endl;
		auto f = __open__(std::string("/tmp/nosuchfile"), std::string("rb"));			/* new variable */
	}
	catch (std::runtime_error* __error__) {
		std::string __errorname__ = __parse_error_type__(__error__);
		if (__errorname__ == std::string("RuntimeError")) {
			__finally_done_1 = true;
				try {		// finally block
					std::cout << std::string("FINALLY") << std::endl;
					b = true;
				} catch (...) {}
			std::cout << std::string("this should not happen") << std::endl;
		}
		if (__errorname__ == std::string("IOError")) {
			__finally_done_1 = true;
				try {		// finally block
					std::cout << std::string("FINALLY") << std::endl;
					b = true;
				} catch (...) {}
			std::cout << std::string("CAUGHT IOError OK") << std::endl;
			return;
		}
					__finally_done_1 = true;
				try {		// finally block
					std::cout << std::string("FINALLY") << std::endl;
					b = true;
				} catch (...) {}
			std::cout << std::string("CAUGHT UNKNOWN EXECEPTION") << std::endl;
			throw RuntimeError(std::string("got unknown exception"));
	}
	if (__finally_done_1 == false) {
		try {		// finally block
			std::cout << std::string("FINALLY") << std::endl;
			b = true;
		} catch (...) {}
	}
	if (!(( b == true ))) {throw std::runtime_error("assertion failed: ( b == true )"); }
}
int main() {

	
	myfunc();
	return 0;
}
```
* [if_else.py](c++/if_else.py)

input:
------
```python
'''
simple if/else
'''


def main():
	a = 'x'
	if a == 'x':
		print('ok')
```
output:
------
```c++

int main() {

	
	auto a = std::string("x");  /* auto-fallback */
	if (( a == std::string("x") )) {
		std::cout << std::string("ok") << std::endl;
	}
	return 0;
}
```