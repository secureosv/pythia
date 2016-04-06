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
		assert arr[0][0] == 1

def main():
	a = make_array()
	print( len(a))
	assert len(a)==2
	assert len(a[0])==3
	assert len(a[1])==5
	test_array(a)
	print 'ok'
```
output:
------
```c++

std::vector<std::vector<int>*>* make_array() {

	
	auto arr = new std::vector<std::vector<int>*>{new std::vector<int> {1,2,3},new std::vector<int> {4,5,6,7,8}};
	return arr;
}
auto test_array(std::vector<std::vector<int>*>* arr) {

	
	if (!(( (*(*arr)[0])[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*(*arr)[0])[0] == 1 )"); }
	/* arrays:
		arr : std::vector<std::vector<int>*>*
*/
}
int main() {

	
	auto a = make_array();			/* new variable*/
	std::cout << a->size() << std::endl;
	if (!(( a->size() == 2 ))) {throw std::runtime_error("assertion failed: ( a->size() == 2 )"); }
	if (!(( (*a)[0]->size() == 3 ))) {throw std::runtime_error("assertion failed: ( (*a)[0]->size() == 3 )"); }
	if (!(( (*a)[1]->size() == 5 ))) {throw std::runtime_error("assertion failed: ( (*a)[1]->size() == 5 )"); }
	test_array(a);
	std::cout << std::string("ok") << std::endl;
	return 0;
}
```
* [pointers_returns_array.py](c++/pointers_returns_array.py)

input:
------
```python
'''
returns pointer to array
'''

def make_array() -> std::vector<int>*:
	arr = new([]int( 1,2,3,4 ))
	return arr

def test_array( arr:std::vector<int>* ):
	print( arr[0] )
	print( arr[1] )
	print( arr[2] )
	print( arr[3] )


with pointers:
	def Pmake_array() -> []int:
		arr = new([]int( 1,2,3,4 ))
		return arr

	def Ptest_array( arr:[]int ):
		print( arr[0] )
		print( arr[1] )
		print( arr[2] )
		print( arr[3] )

def test():
	a = make_array()
	print('arr length:', len(a))
	test_array(a)


def test_pointers():
	a = Pmake_array()
	print('arr length:', len(a))
	Ptest_array(a)

def main():
	test()
	test_pointers()
```
output:
------
```c++

std::vector<int>* make_array() {

	
	auto arr = new std::vector<int>({1,2,3,4});
	return arr;
}
auto test_array(std::vector<int>* arr) {

	
	std::cout << (*arr)[0] << std::endl;
	std::cout << (*arr)[1] << std::endl;
	std::cout << (*arr)[2] << std::endl;
	std::cout << (*arr)[3] << std::endl;
}
std::vector<int>* Pmake_array() {

	
	auto arr = new std::vector<int>({1,2,3,4});
	return arr;
}
auto Ptest_array(std::vector<int>* arr) {

	
	std::cout << (*arr)[0] << std::endl;
	std::cout << (*arr)[1] << std::endl;
	std::cout << (*arr)[2] << std::endl;
	std::cout << (*arr)[3] << std::endl;
	/* arrays:
		arr : std::vector<int>*
*/
}
auto test() {

	
	auto a = make_array();			/* new variable*/
	std::cout << std::string("arr length:");
std::cout << a->size();std::cout << std::endl;
	test_array(a);
}
auto test_pointers() {

	
	auto a = Pmake_array();			/* new variable*/
	std::cout << std::string("arr length:");
std::cout << a->size();std::cout << std::endl;
	Ptest_array(a);
}
int main() {

	
	test();
	test_pointers();
	return 0;
}
```
* [decays_to_pointer.py](c++/decays_to_pointer.py)

input:
------
```python
'''
C fixed size arrays decay to pointers in C++.

'''
with stack:
	class A:
		pass

	class Bar:
		def __init__(self, x:[2]int ):
			#self.x[:] = x  ## this works but is not required
			## the translator is able to detect in this case 
			## that this needs to be an array copy.
			self.x = x

	class Foo( Bar ):
		def __init__(self, x:[2]int, y:[4]A ):
			self.x = x
			self.y = y

	def test_normal_array( arr:[]int )->int:
		return len(arr)

	def test_pointer_decay( arr:[2]int )->int:
		let b : [2]int
		#b[...] = addr(arr[0])  ## error: invalid conversion from ‘int*’ to ‘int’
		#b[...] = arr[0]  ## compiles but fails asserts below

		## explicit copy
		#b[:] = arr
		## in this simple case, the translator knows that `b` is a fixed size array,
		## and that it needs to copy all items from `arr`
		b = arr

		assert b[0]==arr[0]
		assert b[1]==arr[1]
		return len(arr)

	def stack_test():
		let alist : [4]A
		let i4 : [4]int
		i4[0]=1
		i4[1]=2

		i2 = [2]int(10,20)
		assert i2[0]==10
		assert i2[1]==20

		## pointer assignment only catches the first item
		i2[...] = i4[0]
		assert i2[0]==i4[0]
		#assert i2[1]==i4[1]  ## this will fail

		## explicit copy ok
		i2[:] = i4
		assert i2[0]==i4[0]
		assert i2[1]==i4[1]

		test_pointer_decay(i2) == len(i2)

		a = Bar(i2)
		arr = [2]int(6,7)
		b = Bar(arr)
		## test fixed size array assignment from object to object
		assert a.x[0]==i2[0]
		assert a.x[1]==i2[1]
		## direct assignment not allowed
		#a.x = b.x  # error: invalid array assignment
		#a.x[:] = b.x  ## error unknown array fixed size
		a.x[:2] = b.x  ## workaround: slice assignment with upper bound
		assert a.x[0]==b.x[0]
		assert a.x[1]==b.x[1]

def main():
	stack_test()
```
output:
------
```c++

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return __class__;}
};
class Bar: public std::enable_shared_from_this<Bar> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x[2];
	Bar __init__(int x[2]);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Bar() {__class__ = std::string("Bar"); __initialized__ = true; __classid__=2;}
	Bar(bool init) {__class__ = std::string("Bar"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return __class__;}
};
class Foo:  public Bar {
  public:
//	members from class: Bar  ['x']
	A  y[4];
	Foo __init__(int x[2]);
	Foo __init__(int x[2], A y[4]);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true; __classid__=1;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return __class__;}
};
int test_normal_array(std::vector<int>* arr) {

	
	return arr->size();
	/* arrays:
		arr : std::vector<int>*
*/
}
int test_pointer_decay(int arr[2]) {

	
	int b[2] = {0,0};
	b[0] = arr[0]; b[1] = arr[1];
	if (!(( b[0] == arr[0] ))) {throw std::runtime_error("assertion failed: ( b[0] == arr[0] )"); }
	if (!(( b[1] == arr[1] ))) {throw std::runtime_error("assertion failed: ( b[1] == arr[1] )"); }
	return 2;
	/* arrays:
		arr : ('int', '2')
		b : ('int', '2')
*/
}
auto stack_test() {

	
	A alist[4] = {A(false),A(false),A(false),A(false)};
	int i4[4] = {0,0,0,0};
	i4[0] = 1;
	i4[1] = 2;
	int i2[2] = {10,20};
	if (!(( i2[0] == 10 ))) {throw std::runtime_error("assertion failed: ( i2[0] == 10 )"); }
	if (!(( i2[1] == 20 ))) {throw std::runtime_error("assertion failed: ( i2[1] == 20 )"); }
	(*i2) = i4[0];
	if (!(( i2[0] == i4[0] ))) {throw std::runtime_error("assertion failed: ( i2[0] == i4[0] )"); }
	i2[0] = i4[0];
i2[1] = i4[1];
	if (!(( i2[0] == i4[0] ))) {throw std::runtime_error("assertion failed: ( i2[0] == i4[0] )"); }
	if (!(( i2[1] == i4[1] ))) {throw std::runtime_error("assertion failed: ( i2[1] == i4[1] )"); }
	( test_pointer_decay(i2) == 2 );
	auto a = Bar().__init__(i2);			/* new variable*/
	int arr[2] = {6,7};
	auto b = Bar().__init__(arr);			/* new variable*/
	if (!(( a.x[0] == i2[0] ))) {throw std::runtime_error("assertion failed: ( a.x[0] == i2[0] )"); }
	if (!(( a.x[1] == i2[1] ))) {throw std::runtime_error("assertion failed: ( a.x[1] == i2[1] )"); }
	for (int __i=0; __i<2; __i++) {
	  a.x[__i] = b.x[__i];
	}
	if (!(( a.x[0] == b.x[0] ))) {throw std::runtime_error("assertion failed: ( a.x[0] == b.x[0] )"); }
	if (!(( a.x[1] == b.x[1] ))) {throw std::runtime_error("assertion failed: ( a.x[1] == b.x[1] )"); }
	/* arrays:
		arr : ('int', '2')
		i2 : ('int', '2')
		alist : ('A', '4')
		i4 : ('int', '4')
*/
}
	Foo Foo::__init__(int x[2], A y[4]) {

		
		(*this).x[0] = x[0]; (*this).x[1] = x[1];
		(*this).y[0] = y[0]; (*this).y[1] = y[1]; (*this).y[2] = y[2]; (*this).y[3] = y[3];
		return *this;
		/* arrays:
			y : ('A', '4')
			x : ('int', '2')
*/
	}
	Foo Foo::__init__(int x[2]) {

		
		(*this).x[0] = x[0]; (*this).x[1] = x[1];
		return *this;
		/* arrays:
			x : ('int', '2')
*/
	}
	Bar Bar::__init__(int x[2]) {

		
		(*this).x[0] = x[0]; (*this).x[1] = x[1];
		return *this;
		/* arrays:
			x : ('int', '2')
*/
	}
int main() {

	
	stack_test();
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

def some_vec():
	a = []int(1,2,3,4)
	return a

def test_unknown_vectypes():
	print 'testing unknown vec types'
	v1 = some_vec()
	v2 = v1[ 1: ]
	assert v2[0]==2
	assert v2[1]==3
	assert v2[2]==4
	assert len(v2)==3

	v3 = v1[ :2 ]
	assert v3[0]==1
	assert v3[1]==2
	assert len(v3)==2

	v4 = v1[:]
	assert len(v4)==len(v1)
	assert v4[0]==v1[0]

	print 'OK'


def test_known_vectypes():
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
	test_known_vectypes()
	test_unknown_vectypes()
	print('OK')

#main()
```
output:
------
```c++

auto some_vec() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4})) ); /* 1D Array */
	return a;
	/* arrays:
		a : int
*/
}
auto test_unknown_vectypes() {

	
	std::cout << std::string("testing unknown vec types") << std::endl;
	auto v1 = some_vec();			/* new variable*/
	auto v2 = std::make_shared<std::vector<decltype(v1->begin())::value_type>>( std::vector<decltype(v1->begin())::value_type>(v1->begin()+1,v1->end()) );
	if (!(( (*v2)[0] == 2 ))) {throw std::runtime_error("assertion failed: ( (*v2)[0] == 2 )"); }
	if (!(( (*v2)[1] == 3 ))) {throw std::runtime_error("assertion failed: ( (*v2)[1] == 3 )"); }
	if (!(( (*v2)[2] == 4 ))) {throw std::runtime_error("assertion failed: ( (*v2)[2] == 4 )"); }
	if (!(( v2->size() == 3 ))) {throw std::runtime_error("assertion failed: ( v2->size() == 3 )"); }
	auto v3 = std::make_shared<std::vector<decltype(v1->begin())::value_type>>( std::vector<decltype(v1->begin())::value_type>(v1->begin(),v1->begin()+2) );
	if (!(( (*v3)[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*v3)[0] == 1 )"); }
	if (!(( (*v3)[1] == 2 ))) {throw std::runtime_error("assertion failed: ( (*v3)[1] == 2 )"); }
	if (!(( v3->size() == 2 ))) {throw std::runtime_error("assertion failed: ( v3->size() == 2 )"); }
	auto v4 = std::make_shared<std::vector<decltype(v1->begin())::value_type>>( std::vector<decltype(v1->begin())::value_type>(v1->begin(),v1->end()) );
	if (!(( v4->size() == v1->size() ))) {throw std::runtime_error("assertion failed: ( v4->size() == v1->size() )"); }
	if (!(( (*v4)[0] == (*v1)[0] ))) {throw std::runtime_error("assertion failed: ( (*v4)[0] == (*v1)[0] )"); }
	std::cout << std::string("OK") << std::endl;
}
auto test_known_vectypes() {

	
	for (int step=0; step<2; step++) {
		auto w = range1(10);			/* new variable*/
		if (!(( w->size() == 10 ))) {throw std::runtime_error("assertion failed: ( w->size() == 10 )"); }
		if (!(( (*w)[0] == 0 ))) {throw std::runtime_error("assertion failed: ( (*w)[0] == 0 )"); }
		if (!(( (*w)[9] == 9 ))) {throw std::runtime_error("assertion failed: ( (*w)[9] == 9 )"); }
		auto r = range2(10, 20);			/* new variable*/
		if (!(( (*r)[0] == 10 ))) {throw std::runtime_error("assertion failed: ( (*r)[0] == 10 )"); }
		if (!(( (*r)[1] == 11 ))) {throw std::runtime_error("assertion failed: ( (*r)[1] == 11 )"); }
		std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
		std::cout << std::string("a addr:");
std::cout << a;std::cout << std::endl;
		std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
		if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
		/*<<slice>> `a` [1:None:None] int */
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
		/*<<slice>> `a` [None:None:None] int */
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
		/*<<slice>> `a` [None:2:None] int */
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
		/*<<slice>> `a` [None:None:1] int */
std::vector<int> _ref_e;
if(1<0){for(int _i_=a->size()-1;_i_>=0;_i_+=1){ _ref_e.push_back((*a)[_i_]);}} else {for(int _i_=0;_i_<a->size();_i_+=1){ _ref_e.push_back((*a)[_i_]);}}
		std::shared_ptr<std::vector<int>> e = std::make_shared<std::vector<int>>(_ref_e);
		std::cout << std::string("len e should be same<<__as__<<a:");
std::cout << e->size();std::cout << std::endl;
		if (!(( e->size() == a->size() ))) {throw std::runtime_error("assertion failed: ( e->size() == a->size() )"); }
		for (auto &i: (*e)) { /*loop over heap vector*/
			std::cout << i << std::endl;
		}
		/*<<slice>> `a` [None:None:2] int */
std::vector<int> _ref_f;
if(2<0){for(int _i_=a->size()-1;_i_>=0;_i_+=2){ _ref_f.push_back((*a)[_i_]);}} else {for(int _i_=0;_i_<a->size();_i_+=2){ _ref_f.push_back((*a)[_i_]);}}
		std::shared_ptr<std::vector<int>> f = std::make_shared<std::vector<int>>(_ref_f);
		std::cout << std::string("len f:");
std::cout << f->size();std::cout << std::endl;
		if (!(( f->size() == 3 ))) {throw std::runtime_error("assertion failed: ( f->size() == 3 )"); }
		if (!(( (*f)[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*f)[0] == 1 )"); }
		if (!(( (*f)[1] == 3 ))) {throw std::runtime_error("assertion failed: ( (*f)[1] == 3 )"); }
		if (!(( (*f)[2] == 5 ))) {throw std::runtime_error("assertion failed: ( (*f)[2] == 5 )"); }
		/*<<slice>> `a` [None:None:-1] int */
		std::vector<int> _ref_g;
for(int _i_=a->size()-1;_i_>=0;_i_-=1){
 _ref_g.push_back((*a)[_i_]);
}
		std::shared_ptr<std::vector<int>> g = std::make_shared<std::vector<int>>(_ref_g);
		std::cout << std::string("- - - -") << std::endl;
		for (auto &v: (*g)) { /*loop over heap vector*/
			std::cout << v << std::endl;
		}
		std::cout << std::string("len g:");
std::cout << g->size();std::cout << std::endl;
		if (!(( g->size() == a->size() ))) {throw std::runtime_error("assertion failed: ( g->size() == a->size() )"); }
		if (!(( (*g)[0] == 5 ))) {throw std::runtime_error("assertion failed: ( (*g)[0] == 5 )"); }
		if (!(( (*g)[4] == 1 ))) {throw std::runtime_error("assertion failed: ( (*g)[4] == 1 )"); }
		std::cout << std::string("---slice---") << std::endl;
		/*<<slice>> `a` [2:None:-1] int */
		std::vector<int> _ref_h;
for(int _i_=2;_i_>=0;_i_-=1){
 _ref_h.push_back((*a)[_i_]);
}
		std::shared_ptr<std::vector<int>> h = std::make_shared<std::vector<int>>(_ref_h);
		for (auto &i: (*h)) { /*loop over heap vector*/
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
	test_known_vectypes();
	test_unknown_vectypes();
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	A* __init__(int x);
	int method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x']
	B* __init__(int x);
	int foo();
	int method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true; __classid__=2;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x']
	C* __init__(int x);
	int bar();
	int method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true; __classid__=1;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return this->__class__;}
};
	int C::method() {

		
		return this->x;
	}
	int C::bar() {

		
		return (this->x + 200);
	}
	C* C::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int B::method() {

		
		return this->x;
	}
	int B::foo() {

		
		return (this->x * 2);
	}
	B* B::__init__(int x) {

		
		this->x = x;
		return this;
	}
	int A::method() {

		
		return this->x;
	}
	A* A::__init__(int x) {

		
		this->x = x;
		return this;
	}
int main() {

	
	auto a = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(0); return _;}();			/* new variable*/
	auto b = [&](){auto _ = std::shared_ptr<B>(new B()); _->__init__(1); return _;}();			/* new variable*/
	auto c = [&](){auto _ = std::shared_ptr<C>(new C()); _->__init__(2); return _;}();			/* new variable*/
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
auto somefunc() {

	
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
	auto x = std::shared_ptr<A>(new A());			/* new variable*/
	auto y = std::shared_ptr<A>(new A());			/* new variable*/
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
auto stackfunc() {

	
		int a[5] = {1,2,3,4,5};
	std::cout << std::string("sizeof a:");
std::cout << sizeof(a);std::cout << std::endl;
	std::cout << std::string("len a:");
std::cout << 5;std::cout << std::endl;
	std::cout << a[0] << std::endl;
	std::cout << a[1] << std::endl;
	std::cout << std::string("testing iter loop") << std::endl;
	for (int __idx=0; __idx<5; __idx++) { /*loop over fixed array*/
	int val = a[__idx];
		std::cout << val << std::endl;
	}
	std::cout << std::string("slice fixed size array front") << std::endl;
	/* <fixed size slice> 1 : None : None */
	int b[4] = {a[1],a[2],a[3],a[4]};
	if (!(b[0])) {throw std::runtime_error("assertion failed: b[0]"); }
	if (!(( 4 == ( (5 - 1) ) ))) {throw std::runtime_error("assertion failed: ( 4 == ( (5 - 1) ) )"); }
	for (int __idx=0; __idx<4; __idx++) { /*loop over fixed array*/
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
	for (int __idx=0; __idx<2; __idx++) { /*loop over fixed array*/
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
		for (int __idx=0; __idx<N; __idx++) { /*loop over fixed array*/
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
		for (int __idx=0; __idx<N-2; __idx++) { /*loop over fixed array*/
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

auto myfunc(int x) {

	
	std::cout << (x * 100) << std::endl;
}
auto myfunc(std::string x) {

	
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  y;
	int  x;
	A* __init__(int x, int y);
	static auto foo();
	static int bar(int a);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
	int A::bar(int a) {

		
		return (a + 1000);
	}
	auto A::foo() {

		
		std::cout << std::string("my classmethod") << std::endl;
	}
	A* A::__init__(int x, int y) {

		
		this->x = x;
		this->y = y;
		return this;
	}
int main() {

	
	auto x = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(1, 2); return _;}();			/* new variable*/
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
let syntax inspired by rust.
cdef syntax borrowed from cython.
'''

macro( NUM=100 )  ## becomes `#define NUM 100`

class Foo():
	def __init__(self):
		let self.data : [NUM]int

let Foos: []Foo

let TwentyFoos : [20]Foo

mycomp = []int()
twentyints = [20]int()

gFoo = Foo()


def main():
	cdef int a=1
	cdef int b=2
	cdef int *myptr
	assert a+b==3
	a = 10
	assert a+b==12

	print gFoo

	print 'len mycomp:', len(mycomp)
	assert len(mycomp)==0

	mycomp2 = []int()
	mycomp2.append( 10 )
	print 'len mycomp2:', len(mycomp2)
	assert len(mycomp2)==1

	print Foos

	print len(Foos)
	assert len(Foos) == 0

	f = Foo()
	assert len(f.data)==NUM
	f.data[0] = 12
	print f.data[0]

	Foos.push_back(f)
	print len(Foos)
	assert len(Foos)==1

	print len(TwentyFoos)
	TwentyFoos[0] = f
	print TwentyFoos[0]
```
output:
------
```c++

#define NUM 100//;
class Foo: public std::enable_shared_from_this<Foo> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	std::shared_ptr<std::vector<int>>  data;
	Foo* __init__();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true; __classid__=0;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
auto Foos = std::make_shared<std::vector<std::shared_ptr<Foo>>>();
auto TwentyFoos = std::make_shared<std::vector<std::shared_ptr<Foo>>>(20);
auto mycomp = std::make_shared<std::vector<int>>();
auto twentyints = std::make_shared<std::vector<int>>(20);
auto gFoo = [&](){auto _ = std::shared_ptr<Foo>(new Foo()); _->__init__(); return _;}();
	Foo* Foo::__init__() {

		
		this->data = std::make_shared<std::vector<int>>(NUM);
		return this;
		/* arrays:
			TwentyFoos : ('Foo', '20')
*/
	}
int main() {

	
	int a=1;
	int b=2;
	int *myptr;
	if (!(( ( (a + b) ) == 3 ))) {throw std::runtime_error("assertion failed: ( ( (a + b) ) == 3 )"); }
	a = 10;
	if (!(( ( (a + b) ) == 12 ))) {throw std::runtime_error("assertion failed: ( ( (a + b) ) == 12 )"); }
	std::cout << gFoo << std::endl;
	std::cout << std::string("len mycomp:");
std::cout << mycomp->size();std::cout << std::endl;
	if (!(( mycomp->size() == 0 ))) {throw std::runtime_error("assertion failed: ( mycomp->size() == 0 )"); }
	std::shared_ptr<std::vector<int>> mycomp2( (new std::vector<int>({})) ); /* 1D Array */
	mycomp2->push_back(10);
	std::cout << std::string("len mycomp2:");
std::cout << mycomp2->size();std::cout << std::endl;
	if (!(( mycomp2->size() == 1 ))) {throw std::runtime_error("assertion failed: ( mycomp2->size() == 1 )"); }
	std::cout << Foos << std::endl;
	std::cout << Foos->size() << std::endl;
	if (!(( Foos->size() == 0 ))) {throw std::runtime_error("assertion failed: ( Foos->size() == 0 )"); }
	auto f = [&](){auto _ = std::shared_ptr<Foo>(new Foo()); _->__init__(); return _;}();			/* new variable*/
	if (!(( f->data->size() == NUM ))) {throw std::runtime_error("assertion failed: ( f->data->size() == NUM )"); }
	(*f->data)[0] = 12;
	std::cout << (*f->data)[0] << std::endl;
	Foos->push_back(f);
	std::cout << Foos->size() << std::endl;
	if (!(( Foos->size() == 1 ))) {throw std::runtime_error("assertion failed: ( Foos->size() == 1 )"); }
	std::cout << TwentyFoos->size() << std::endl;
	(*TwentyFoos)[0] = f;
	std::cout << (*TwentyFoos)[0] << std::endl;
	return 0;
	/* arrays:
		mycomp2 : int
		TwentyFoos : ('Foo', '20')
*/
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
	for (auto &item: (*a)) { /*loop over heap vector*/
		std::cout << item << std::endl;
	}
	return 0;
	/* arrays:
		a : int
*/
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

	
	auto i = 10;  /* auto-fallback <_ast.Num object at 0x7fc34f7e2350> */
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<A>  a = nullptr;
int b = 0;
auto check_globals() {

	
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
* [shared_from_this.py](c++/shared_from_this.py)

input:
------
```python
'''
std::enable_shared_from_this
tests passing shared pointer to self to other functions,
and subclasses that use std::static_pointer_cast to convert
function arguments.
'''


class Foo():
	def __init__(self, x:int):
		self.x = x
		let self.other : Foo = None

	def bar(self) -> int:
		return self.x

	def test(self) ->int:
		return callbar( self.shared_from_this() )

def callbar( o:Foo ) -> int:
	return o.bar()

class Sub( Foo ):
	def __init__(self, x:int, o:Foo ):
		self.x = x
		o.other = shared_from_this()

	def submethod(self) -> int:
		a = callbar( self.shared_from_this() )
		return a * 2
	def sub(self) -> int:
		return self.x -1

	## returns self.sub()
	def testsub(self) -> int:
		return callsub( shared_from_this() )

	## returns self.sub()
	def test_pass_self(self) -> int:
		return self.callsub( shared_from_this() )

	def callsub(self, other:Sub) -> int:
		return other.sub()


def callsub( s:Sub ) -> int:
	return s.sub()


def main():
	f = Foo(10)
	assert f.test()==10

	s = Sub(100, f)
	print 'should be 100:', s.test()
	assert s.test()==100
	assert s.submethod()==200
	assert s.testsub()==99
	assert s.test_pass_self()==99

	ss = Sub(
		10,
		Sub(100, Sub(1))
	)
	#sa = Sub(1)
	#ss = Sub(10,sa)
	print ss
	assert ss.x==10
	assert ss.test_pass_self()==9

	Sub(10,Sub(11))
	#Sub(10,Sub(100, Sub(1)))  ## TODO nested > 1 levels

	#Sub( Sub(10).sub() )  ## this is not allowed
	sss = Sub( Sub(10).sub() )  ## this works but is not always shared_from_this
	#sss = Sub(1, Sub(10).shared_from_this() )  ## this fails

	let subs : [10]Sub
	ptr = subs[0]
	assert ptr is None
	ps = ptr as Sub
	assert ps is None
	pss = ptr as Foo
	assert pss is None
```
output:
------
```c++

class Foo: public std::enable_shared_from_this<Foo> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	std::shared_ptr<Foo>  other;
	Foo* __init__(int x);
	int bar();
	int test();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true; __classid__=0;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
int callbar(std::shared_ptr<Foo> o) {

	
	return o->bar();
}
class Sub:  public Foo {
  public:
//	members from class: Foo  ['x', 'other']
	std::shared_ptr<Foo>  o;
	Sub* __init__(int x);
	Sub* __init__(int x, std::shared_ptr<Foo> o);
	int submethod();
	int sub();
	int testsub();
	int test_pass_self();
	int callsub(std::shared_ptr<Sub> other);
	inline int callsub(std::shared_ptr<Foo> other){ return callsub(
std::static_pointer_cast<Sub>(other));}
	int bar();
	int test();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Sub() {__class__ = std::string("Sub"); __initialized__ = true; __classid__=1;}
	Sub(bool init) {__class__ = std::string("Sub"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return this->__class__;}
};
int callsub(std::shared_ptr<Foo> __s){
auto s = std::static_pointer_cast<Sub>(__s);

return s->sub();
}
int callsub(std::shared_ptr<Sub> s) {

	
	return s->sub();
}
	int Sub::test() {

		
		return callbar(this->shared_from_this());
	}
	int Sub::bar() {

		
		return this->x;
	}
	int Sub::callsub(std::shared_ptr<Sub> other) {

		
		return other->sub();
	}
	int Sub::test_pass_self() {

		
		return this->callsub(shared_from_this());
	}
	int Sub::testsub() {

		
		return callsub(shared_from_this());
	}
	int Sub::sub() {

		
		return (this->x - 1);
	}
	int Sub::submethod() {

		
		auto a = callbar(this->shared_from_this());			/* new variable*/
		return (a * 2);
	}
	Sub* Sub::__init__(int x, std::shared_ptr<Foo> o) {

		
		this->x = x;
		o->other = shared_from_this();
		return this;
	}
	Sub* Sub::__init__(int x) {

		
		this->x = x;
		this->other = nullptr;
		return this;
	}
	int Foo::test() {

		
		return callbar(this->shared_from_this());
	}
	int Foo::bar() {

		
		return this->x;
	}
	Foo* Foo::__init__(int x) {

		
		this->x = x;
		this->other = nullptr;
		return this;
	}
int main() {

	
	auto f = [&](){auto _ = std::shared_ptr<Foo>(new Foo()); _->__init__(10); return _;}();			/* new variable*/
	if (!(( f->test() == 10 ))) {throw std::runtime_error("assertion failed: ( f->test() == 10 )"); }
	auto s = [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(100, f); return _;}();			/* new variable*/
	std::cout << std::string("should be 100:");
std::cout << s->test();std::cout << std::endl;
	if (!(( s->test() == 100 ))) {throw std::runtime_error("assertion failed: ( s->test() == 100 )"); }
	if (!(( s->submethod() == 200 ))) {throw std::runtime_error("assertion failed: ( s->submethod() == 200 )"); }
	if (!(( s->testsub() == 99 ))) {throw std::runtime_error("assertion failed: ( s->testsub() == 99 )"); }
	if (!(( s->test_pass_self() == 99 ))) {throw std::runtime_error("assertion failed: ( s->test_pass_self() == 99 )"); }
	auto ss = [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(10, [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(100, [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(1); return _;}()); return _;}()); return _;}();			/* new variable*/
	std::cout << ss << std::endl;
	if (!(( ss->x == 10 ))) {throw std::runtime_error("assertion failed: ( ss->x == 10 )"); }
	if (!(( ss->test_pass_self() == 9 ))) {throw std::runtime_error("assertion failed: ( ss->test_pass_self() == 9 )"); }
	[&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(10, [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(11); return _;}()); return _;}();
	auto sss = [&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__([&](){auto _ = std::shared_ptr<Sub>(new Sub()); _->__init__(10); return _;}()->sub()); return _;}();			/* new variable*/
	auto subs = std::make_shared<std::vector<std::shared_ptr<Sub>>>(10);
	auto ptr = (*subs)[0];  /* auto-fallback <_ast.Subscript object at 0x7f86f8fd7650> */
	if (!(( ptr == nullptr ))) {throw std::runtime_error("assertion failed: ( ptr == nullptr )"); }
		auto ps = std::static_pointer_cast<Sub>(ptr);
	if (!(( ps == nullptr ))) {throw std::runtime_error("assertion failed: ( ps == nullptr )"); }
		auto pss = std::static_pointer_cast<Foo>(ptr);
	if (!(( pss == nullptr ))) {throw std::runtime_error("assertion failed: ( pss == nullptr )"); }
	return 0;
	/* arrays:
		subs : ('Sub', '10')
*/
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
		[1,2,3],
		[4,5,6,7,8],
		None,
		#(x*x for x in range(4)),  ## TODO fix listcomps
		(x for x in range(20)),
	)

	a,b,c = arr[0]
	assert a==1
	assert b==2
	assert c==3

	for vec in arr:
		print vec
		if vec is not None:
			x,y,z = vec
			print x,y,z

	assert len(arr)==4
	assert len(arr[0])==3
	assert len(arr[1])==5
	assert len(arr[3])==20
	assert arr[2] is None

	v = 1
	for i in arr[0]:
		assert i==v
		v+=1

	sub = arr[1]
	v = sub[0]
	for i in sub:
		assert i == v
		v+=1

	v = 0
	for i in arr[3]:
		assert i==v
		v+=1

	arr[3][0] = 1000
	arr[3][1] = 1001

	assert arr[3][0] == 1000
	assert arr[3][1] == 1001

	print 'OK'
```
output:
------
```c++

int main() {

	
	/* arr = vector of vectors to: int */	
std::vector<int> _comp__subcomp_arr; /*comprehension*/
	for (int x=0; x<20; x++) {
		_comp__subcomp_arr.push_back(x);
	}
	auto _subcomp_arr = std::make_shared<std::vector<int>>(_comp__subcomp_arr);	
	auto arr = std::make_shared<std::vector<std::shared_ptr<std::vector<int>>>>(std::vector<std::shared_ptr<std::vector<int>>>{		std::shared_ptr<std::vector<int>>(new std::vector<int>{1,2,3}),
		std::shared_ptr<std::vector<int>>(new std::vector<int>{4,5,6,7,8}),
		nullptr,
		_subcomp_arr});
	
	auto __r_0 = (*arr)[0];  /* auto-fallback <_ast.Subscript object at 0x7fcfe936dd50> */
	auto a = (*__r_0)[0];  /* auto-fallback <_ast.Subscript object at 0x7fcfe936ded0> */
	auto b = (*__r_0)[1];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92fe090> */
	auto c = (*__r_0)[2];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92fe210> */
	if (!(( a == 1 ))) {throw std::runtime_error("assertion failed: ( a == 1 )"); }
	if (!(( b == 2 ))) {throw std::runtime_error("assertion failed: ( b == 2 )"); }
	if (!(( c == 3 ))) {throw std::runtime_error("assertion failed: ( c == 3 )"); }
	for (auto &vec: (*arr)) { /*loop over heap vector*/
		std::cout << vec << std::endl;
		if (( vec != nullptr )) {
			auto x = (*vec)[0];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92fe8d0> */
			auto y = (*vec)[1];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92fea50> */
			auto z = (*vec)[2];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92febd0> */
			std::cout << x;
std::cout << y;
std::cout << z;std::cout << std::endl;
		}
	}
	if (!(( arr->size() == 4 ))) {throw std::runtime_error("assertion failed: ( arr->size() == 4 )"); }
	if (!(( (*arr)[0]->size() == 3 ))) {throw std::runtime_error("assertion failed: ( (*arr)[0]->size() == 3 )"); }
	if (!(( (*arr)[1]->size() == 5 ))) {throw std::runtime_error("assertion failed: ( (*arr)[1]->size() == 5 )"); }
	if (!(( (*arr)[3]->size() == 20 ))) {throw std::runtime_error("assertion failed: ( (*arr)[3]->size() == 20 )"); }
	if (!(( (*arr)[2] == nullptr ))) {throw std::runtime_error("assertion failed: ( (*arr)[2] == nullptr )"); }
	auto v = 1;  /* auto-fallback <_ast.Num object at 0x7fcfe92ff8d0> */
	for (auto &i: *(*arr)[0]) { /*loop over unknown type*/
		if (!(( i == v ))) {throw std::runtime_error("assertion failed: ( i == v )"); }
		v ++;
	}
	auto sub = (*arr)[1];  /* auto-fallback <_ast.Subscript object at 0x7fcfe92ffcd0> */
	v = (*sub)[0];
	for (auto &i: *sub) { /*loop over unknown type*/
		if (!(( i == v ))) {throw std::runtime_error("assertion failed: ( i == v )"); }
		v ++;
	}
	v = 0;
	for (auto &i: *(*arr)[3]) { /*loop over unknown type*/
		if (!(( i == v ))) {throw std::runtime_error("assertion failed: ( i == v )"); }
		v ++;
	}
	(*(*arr)[3])[0] = 1000;
	(*(*arr)[3])[1] = 1001;
	if (!(( (*(*arr)[3])[0] == 1000 ))) {throw std::runtime_error("assertion failed: ( (*(*arr)[3])[0] == 1000 )"); }
	if (!(( (*(*arr)[3])[1] == 1001 ))) {throw std::runtime_error("assertion failed: ( (*(*arr)[3])[1] == 1001 )"); }
	std::cout << std::string("OK") << std::endl;
	return 0;
	/* arrays:
		arr : int
		_subcomp_arr : int
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  y;
	int  x;
	A* __init__(int x, int y);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
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

	
	auto x = create_A();			/* new variable*/
	std::cout << x << std::endl;
	std::cout << x->x << std::endl;
	std::cout << x->y << std::endl;
	return 0;
}
```
* [math.py](c++/math.py)

input:
------
```python
'''
basic math
'''

def main():
	sixteen = 2**4
	print sixteen
	assert sixteen == 16

	c = complex(1,2)
	print c
```
output:
------
```c++

int main() {

	
	auto sixteen = std::pow(2, 4);  /* auto-fallback <_ast.Call object at 0x7fbf67055390> */
	std::cout << sixteen << std::endl;
	if (!(( sixteen == 16 ))) {throw std::runtime_error("assertion failed: ( sixteen == 16 )"); }
	auto c = std::complex<double>(1,2);			/* new variable*/
	std::cout << c << std::endl;
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

auto sender_wrapper(int a, cpp::channel<int>  send) {

	
	std::cout << std::string("sending") << std::endl;
	auto result = 100;  /* auto-fallback <_ast.Num object at 0x7fc4ff040590> */
	send.send(result);
}
int recv_wrapper(int a, cpp::channel<int> recver) {

	
	std::cout << std::string("receiving") << std::endl;
	auto v = recver.recv();
	return v;
}
int main() {

	
	std::cout << std::string("enter main") << std::endl;
	auto c = cpp::channel<int>{};			/* new variable*/
	std::cout << std::string("new channel") << std::endl;
	std::cout << std::string("doing spawn thread") << std::endl;
	std::thread __thread0__( [=]{sender_wrapper(17, c);} );
	std::cout << std::string("done spawning thread") << std::endl;
	auto x = recv_wrapper(2, c);			/* new variable*/
	std::cout << x << std::endl;
	if (!(( x == 100 ))) {throw std::runtime_error("assertion failed: ( x == 100 )"); }
	std::cout << std::string("ok") << std::endl;
	if (__thread0__.joinable()) __thread0__.join();
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

auto somefunc() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
	if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
	std::shared_ptr<std::vector<int>> b( (new std::vector<int>({6,7,8,9,10})) ); /* 1D Array */
	if (!(( b->size() == 5 ))) {throw std::runtime_error("assertion failed: ( b->size() == 5 )"); }
	std::shared_ptr<std::vector<int>> c( (new std::vector<int>({100,200})) ); /* 1D Array */
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	std::cout << std::string("slice assign front") << std::endl;
	auto lena = a->size();			/* new variable*/
	auto two = 2;  /* auto-fallback <_ast.Num object at 0x7fe2afacf390> */
	if ((two + 1) >= a->size()) { a->erase(a->begin(), a->end());
} else { a->erase(a->begin(), a->begin()+(two + 1)); }
a->insert(a->begin(), b->begin(), b->end());
	std::cout << std::string("len a:");
std::cout << a->size();std::cout << std::endl;
	if (!(( a->size() == ( ((lena - (two + 1)) + b->size()) ) ))) {throw std::runtime_error("assertion failed: ( a->size() == ( ((lena - (two + 1)) + b->size()) ) )"); }
	for (auto &i: (*a)) { /*loop over heap vector*/
		std::cout << i << std::endl;
	}
	if (!(( (*a)[0] == 6 ))) {throw std::runtime_error("assertion failed: ( (*a)[0] == 6 )"); }
	if (!(( (*a)[5] == 4 ))) {throw std::runtime_error("assertion failed: ( (*a)[5] == 4 )"); }
	if (!(( (*a)[6] == 5 ))) {throw std::runtime_error("assertion failed: ( (*a)[6] == 5 )"); }
	std::cout << std::string("slice assign back") << std::endl;
	b->erase(b->begin()+2, b->end());
b->insert(b->end(), c->begin(), c->end());
	for (auto &i: (*b)) { /*loop over heap vector*/
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
	for (auto &v: (*a)) { /*loop over heap vector*/
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
auto stackfunc() {

	
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
	for (int __idx=0; __idx<5; __idx++) { /*loop over fixed array*/
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

	## TODO: find out why `void` must be returned here, and `auto` fails with this error:
	## error: use of ‘auto Parent::say(std::string)’ before deduction of ‘auto’
	## this->parent.lock()->say(std::string("hello parent"));
	#def say(self, msg:string):
	def say(self, msg:string) ->void:
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

class Parent: public std::enable_shared_from_this<Parent> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  y;
	std::shared_ptr<std::vector<std::shared_ptr<Child>>>  children;
	Parent* __init__(int y, std::shared_ptr<std::vector<std::shared_ptr<Child>>> children);
	std::shared_ptr<Child> create_child(int x, std::shared_ptr<Parent> parent);
	void say(std::string msg);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Parent() {__class__ = std::string("Parent"); __initialized__ = true; __classid__=0;}
	Parent(bool init) {__class__ = std::string("Parent"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
class Child: public std::enable_shared_from_this<Child> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	std::weak_ptr<Parent>  parent;
	Child* __init__(int x, std::shared_ptr<Parent> parent);
	int foo();
	auto bar();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Child() {__class__ = std::string("Child"); __initialized__ = true; __classid__=1;}
	Child(bool init) {__class__ = std::string("Child"); __initialized__ = init; __classid__=1;}
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
	auto Child::bar() {

		
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

		
		auto child = [&](){auto _ = std::shared_ptr<Child>(new Child()); _->__init__(x, parent); return _;}();			/* new variable*/
		this->children->push_back(child);
		return child;
	}
	Parent* Parent::__init__(int y, std::shared_ptr<std::vector<std::shared_ptr<Child>>> children) {

		
		this->children = children;
		this->y = y;
		return this;
		/* arrays:
			children : std::shared_ptr<std::vector<std::shared_ptr<Child>>>
*/
	}
int main() {

	
	std::shared_ptr<std::vector<std::shared_ptr<Child>>> children( ( new std::vector<std::shared_ptr<Child>>({}) ) ); /* 1D Array */
	auto p = [&](){auto _ = std::shared_ptr<Parent>(new Parent()); _->__init__(1000, children); return _;}();			/* new variable*/
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
* [returns_auto.py](c++/returns_auto.py)

input:
------
```python
'''
returns auto
'''

def returns_void() -> void:
	print 'returns void'

def returns_nothing():
	print 'returns nothing'


## this test fails is flag is not typed as `bool`
## g++ will compile with flag untyped (defaults to `auto`),
## but the test will fail when run.
#def returns_int(flag):
def returns_int(flag:bool):
	if flag:
		return 1
	else:
		return 2

def returns_float():
	return 1.1

class Foo:
	def __init__(self, bar:int):
		self.bar = bar
	def get_int(self):
		return 3
	def get_float(self):
		return 4.4
	def do_nothing(self):
		pass
	def get_self(self):
		return self


with stack:
	class FooStack:
		def __init__(self, bar:int):
			self.bar = bar
		def get_self(self):
			return self
		def test_indirect(self):
			return self.test_abstract()

		#@abstractmethod
		def test_abstract(self):
			return self


	class FooStackA( FooStack ):
		def __init__(self, bar:int, value:string):
			self.bar = bar
			self.value = value
		## subclasses automatically generate this
		#def get_self(self):
		#	return self
		## subclasses automatically generate this
		#def test_indirect(self):
		#	return self.test_abstract()
		## subclasses automatically generate this
		#def test_abstract(self):
		#	return self

	class FooStackB( FooStack ):
		def __init__(self, bar:int, value:int):
			self.bar = bar
			self.value = value


def main():
	print returns_int( False )
	assert returns_int( False )==2
	assert returns_int( True )==1
	assert returns_float() == 1.1

	f = Foo(400)
	assert f.get_int()==3
	assert f.get_float()==4.4
	f.do_nothing()
	assert f.bar==400
	assert f.get_self().bar==400

	with stack:
		sf = FooStack(100)
		assert sf.bar==100
		assert sf.get_self().bar==100

		subf = FooStackA(10, 'hello')
		print subf.bar
		print subf.value
		assert subf.bar == 10
		assert subf.value == 'hello'
		o = subf.get_self()
		assert o.bar == 10
		assert o.value == 'hello'

		print o.bar
		print o.value

		## explicit casting to FooStackSub is not required if subclass contains its own versions
		## of methods from its parent classes, these are auto generated durring translation.
		x = o.test_indirect()
		assert x.bar == 10
		assert x.value == 'hello'


		sub = FooStackB(10, 4)
		assert sub.bar == 10
		assert sub.value == 4
		oo = sub.get_self()
		assert oo.bar == 10
		assert oo.value == 4

		print oo.bar
		print oo.value

		## explicit casting to FooStackSub is not required if subclass contains its own versions
		## of methods from its parent classes, these are auto generated durring translation.
		xx = oo.test_indirect()
		assert xx.bar == 10
		assert xx.value == 4

		#assert isinstance(xx, FooStackB)  ## TODO: fixme
		if isinstance(xx, FooStackB):
			print 'xx is FooStackB'
		else:
			raise RuntimeError('test failed')

	print('OK')

```
output:
------
```c++

void returns_void() {

	
	std::cout << std::string("returns void") << std::endl;
}
auto returns_nothing() {

	
	std::cout << std::string("returns nothing") << std::endl;
}
auto returns_int(bool flag) {

	
	if (flag==true) {
		return 1;
	} else {
		return 2;
	}
}
auto returns_float() {

	
	return 1.1;
}
class Foo: public std::enable_shared_from_this<Foo> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  bar;
	Foo* __init__(int bar);
	auto get_int();
	auto get_float();
	auto do_nothing();
	auto get_self();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true; __classid__=2;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return this->__class__;}
};
class FooStack: public std::enable_shared_from_this<FooStack> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  bar;
	FooStack __init__(int bar);
	auto get_self();
	auto test_indirect();
	auto test_abstract();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	FooStack() {__class__ = std::string("FooStack"); __initialized__ = true; __classid__=0;}
	FooStack(bool init) {__class__ = std::string("FooStack"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return __class__;}
};
class FooStackA:  public FooStack {
  public:
//	members from class: FooStack  ['bar']
	std::string  value;
	FooStackA __init__(int bar);
	FooStackA __init__(int bar, std::string value);
	auto get_self();
	auto test_indirect();
	auto test_abstract();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	FooStackA() {__class__ = std::string("FooStackA"); __initialized__ = true; __classid__=1;}
	FooStackA(bool init) {__class__ = std::string("FooStackA"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return __class__;}
};
class FooStackB:  public FooStack {
  public:
//	members from class: FooStack  ['bar']
	int  value;
	FooStackB __init__(int bar);
	FooStackB __init__(int bar, int value);
	auto get_self();
	auto test_indirect();
	auto test_abstract();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	FooStackB() {__class__ = std::string("FooStackB"); __initialized__ = true; __classid__=3;}
	FooStackB(bool init) {__class__ = std::string("FooStackB"); __initialized__ = init; __classid__=3;}
	std::string getclassname() {return __class__;}
};
	auto FooStackB::test_abstract() {

		
		return *this;;
	}
	auto FooStackB::test_indirect() {

		
		return (*this).test_abstract();
	}
	auto FooStackB::get_self() {

		
		return *this;;
	}
	FooStackB FooStackB::__init__(int bar, int value) {

		
		(*this).bar = bar;
		(*this).value = value;
		return *this;
	}
	FooStackB FooStackB::__init__(int bar) {

		
		(*this).bar = bar;
		return *this;
	}
	auto FooStackA::test_abstract() {

		
		return *this;;
	}
	auto FooStackA::test_indirect() {

		
		return (*this).test_abstract();
	}
	auto FooStackA::get_self() {

		
		return *this;;
	}
	FooStackA FooStackA::__init__(int bar, std::string value) {

		
		(*this).bar = bar;
		(*this).value = value;
		return *this;
	}
	FooStackA FooStackA::__init__(int bar) {

		
		(*this).bar = bar;
		return *this;
	}
	auto FooStack::test_abstract() {

		
		return *this;;
	}
	auto FooStack::test_indirect() {

		
		return (*this).test_abstract();
	}
	auto FooStack::get_self() {

		
		return *this;;
	}
	FooStack FooStack::__init__(int bar) {

		
		(*this).bar = bar;
		return *this;
	}
	auto Foo::get_self() {

		
		return std::static_pointer_cast<Foo>(shared_from_this());
	}
	auto Foo::do_nothing() {

		
		/*pass*/
	}
	auto Foo::get_float() {

		
		return 4.4;
	}
	auto Foo::get_int() {

		
		return 3;
	}
	Foo* Foo::__init__(int bar) {

		
		this->bar = bar;
		return this;
	}
int main() {

	
	std::cout << returns_int(false) << std::endl;
	if (!(( returns_int(false) == 2 ))) {throw std::runtime_error("assertion failed: ( returns_int(false) == 2 )"); }
	if (!(( returns_int(true) == 1 ))) {throw std::runtime_error("assertion failed: ( returns_int(true) == 1 )"); }
	if (!(( returns_float() == 1.1 ))) {throw std::runtime_error("assertion failed: ( returns_float() == 1.1 )"); }
	auto f = [&](){auto _ = std::shared_ptr<Foo>(new Foo()); _->__init__(400); return _;}();			/* new variable*/
	if (!(( f->get_int() == 3 ))) {throw std::runtime_error("assertion failed: ( f->get_int() == 3 )"); }
	if (!(( f->get_float() == 4.4 ))) {throw std::runtime_error("assertion failed: ( f->get_float() == 4.4 )"); }
	f->do_nothing();
	if (!(( f->bar == 400 ))) {throw std::runtime_error("assertion failed: ( f->bar == 400 )"); }
	if (!(( f->get_self()->bar == 400 ))) {throw std::runtime_error("assertion failed: ( f->get_self()->bar == 400 )"); }
		auto sf = FooStack().__init__(100);			/* new variable*/
	if (!(( sf.bar == 100 ))) {throw std::runtime_error("assertion failed: ( sf.bar == 100 )"); }
	if (!(( sf.get_self().bar == 100 ))) {throw std::runtime_error("assertion failed: ( sf.get_self().bar == 100 )"); }
	auto subf = FooStackA().__init__(10, std::string("hello"));			/* new variable*/
	std::cout << subf.bar << std::endl;
	std::cout << subf.value << std::endl;
	if (!(( subf.bar == 10 ))) {throw std::runtime_error("assertion failed: ( subf.bar == 10 )"); }
	if (!(( subf.value == std::string("hello") ))) {throw std::runtime_error("assertion failed: ( subf.value == std::string(\"hello\") )"); }
	auto o = subf.get_self();			/* subf   */
	if (!(( o.bar == 10 ))) {throw std::runtime_error("assertion failed: ( o.bar == 10 )"); }
	if (!(( o.value == std::string("hello") ))) {throw std::runtime_error("assertion failed: ( o.value == std::string(\"hello\") )"); }
	std::cout << o.bar << std::endl;
	std::cout << o.value << std::endl;
	auto x = o.test_indirect();			/* o   */
	if (!(( x.bar == 10 ))) {throw std::runtime_error("assertion failed: ( x.bar == 10 )"); }
	if (!(( x.value == std::string("hello") ))) {throw std::runtime_error("assertion failed: ( x.value == std::string(\"hello\") )"); }
	auto sub = FooStackB().__init__(10, 4);			/* new variable*/
	if (!(( sub.bar == 10 ))) {throw std::runtime_error("assertion failed: ( sub.bar == 10 )"); }
	if (!(( sub.value == 4 ))) {throw std::runtime_error("assertion failed: ( sub.value == 4 )"); }
	auto oo = sub.get_self();			/* sub   */
	if (!(( oo.bar == 10 ))) {throw std::runtime_error("assertion failed: ( oo.bar == 10 )"); }
	if (!(( oo.value == 4 ))) {throw std::runtime_error("assertion failed: ( oo.value == 4 )"); }
	std::cout << oo.bar << std::endl;
	std::cout << oo.value << std::endl;
	auto xx = oo.test_indirect();			/* oo   */
	if (!(( xx.bar == 10 ))) {throw std::runtime_error("assertion failed: ( xx.bar == 10 )"); }
	if (!(( xx.value == 4 ))) {throw std::runtime_error("assertion failed: ( xx.value == 4 )"); }
	if ((xx.__class__==std::string("FooStackB"))) {
		auto _cast_xx = static_cast<FooStackB>(xx);
		std::cout << std::string("xx is FooStackB") << std::endl;
	} else {
		throw RuntimeError(std::string("test failed"));
	}
	std::cout << std::string("OK") << std::endl;
	return 0;
}
```
* [stack_mode.py](c++/stack_mode.py)

input:
------
```python
'''
stack memory mode
'''
with stack:
	let garr : [10]int
	grange = range(3)
	class Bar:
		def __init__(self, value:string):
			self.value = value

	class Foo:
		def __init__(self, ok:bool):
			self.ok = ok
			let self.arr1:  [4]Bar

	class Sub(Foo):
		def __init__(self, arr2:[4]Bar):
			#self.arr2[...] = arr2   ## should work but fails
			#self.arr2[...] = addr(arr2[0])  ## should also but work fails
			## workaround, copy data
			self.arr2[:] = arr2

	let Foos : [10]Foo


	def test_foos_vec( arr:[]Foo ):
		assert len(arr)==10
		for item in arr:
			assert item is None
			## in stack mode classes `act-like None`
			assert item.ok is False

	def test_foos_fixedarr( arr:[10]Foo):
		assert len(arr)==10
		for item in arr:
			assert item.ok is False

	def stack_test():
		let bars : [4]Bar
		bars[0] = Bar('hello')
		bars[1] = Bar('world')
		sub = Sub(bars)
		print bars[0].value
		print sub.arr2[0].value


		test_foos_fixedarr(Foos)

		with stdvec as 'std::vector<Foo>(std::begin(%s), std::end(%s))':
			vec = stdvec(Foos, Foos)
			test_foos_vec(addr(vec))

		let arr : [5]int
		for i in garr:
			print i
			assert i==0
		print 'global array iter ok'
		for i in arr:
			print i
			assert i==0
		print 'local array iter ok'

		j = 0
		for i in grange:
			print i
			assert i==j
			j+=1

		print 'loop over global range ok'

		for f in Foos:
			assert f is None
		print 'foos initalized to None ok'

		comp = [ Bar('hello') for i in range(10) ]
		assert len(comp)==10
		comp.append( Bar('world') )
		assert len(comp)==11

		s = []Bar()
		s.append( Bar('xxx') )
		assert len(s)==1



def main():
	j = 0
	for i in grange:
		print i
		assert i==j
		j+=1

	stack_test()
```
output:
------
```c++

int garr[10] = {0,0,0,0,0,0,0,0,0,0};
auto grange = __range1__(3);
class Bar: public std::enable_shared_from_this<Bar> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	std::string  value;
	Bar __init__(std::string value);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Bar() {__class__ = std::string("Bar"); __initialized__ = true; __classid__=1;}
	Bar(bool init) {__class__ = std::string("Bar"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return __class__;}
};
class Foo: public std::enable_shared_from_this<Foo> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	bool  ok;
	Bar  arr1[4];
	Foo __init__(bool ok);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Foo() {__class__ = std::string("Foo"); __initialized__ = true; __classid__=0;}
	Foo(bool init) {__class__ = std::string("Foo"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return __class__;}
};
class Sub:  public Foo {
  public:
//	members from class: Foo  ['ok', 'arr1']
	Bar  arr2[4];
	Sub __init__(Bar arr2[4]);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Sub() {__class__ = std::string("Sub"); __initialized__ = true; __classid__=2;}
	Sub(bool init) {__class__ = std::string("Sub"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return __class__;}
};
Foo Foos[10] = {Foo(false),Foo(false),Foo(false),Foo(false),Foo(false),Foo(false),Foo(false),Foo(false),Foo(false),Foo(false)};
auto test_foos_vec(std::vector<Foo>* arr) {

	
	if (!(( arr->size() == 10 ))) {throw std::runtime_error("assertion failed: ( arr->size() == 10 )"); }
	for (auto &item: (*arr)) { /*loop over heap vector*/
		if (!(( item == nullptr ))) {throw std::runtime_error("assertion failed: ( item == nullptr )"); }
		if (!(( item.ok == false ))) {throw std::runtime_error("assertion failed: ( item.ok == false )"); }
	}
	/* arrays:
		grange : int
		arr : std::vector<Foo>*
		garr : ('int', '10')
		Foos : ('Foo', '10')
*/
}
auto test_foos_fixedarr(Foo arr[10]) {

	
	if (!(( 10 == 10 ))) {throw std::runtime_error("assertion failed: ( 10 == 10 )"); }
	for (int __idx=0; __idx<10; __idx++) { /*loop over fixed array*/
	Foo item = arr[__idx];
		if (!(( item.ok == false ))) {throw std::runtime_error("assertion failed: ( item.ok == false )"); }
	}
	/* arrays:
		grange : int
		arr : ('Foo', '10')
		garr : ('int', '10')
		Foos : ('Foo', '10')
*/
}
auto stack_test() {

	
	Bar bars[4] = {Bar(false),Bar(false),Bar(false),Bar(false)};
	bars[0] = Bar().__init__(std::string("hello"));
	bars[1] = Bar().__init__(std::string("world"));
	auto sub = Sub().__init__(bars);			/* new variable*/
	std::cout << bars[0].value << std::endl;
	std::cout << sub.arr2[0].value << std::endl;
	test_foos_fixedarr(Foos);
	auto vec = std::vector<Foo>(std::begin(Foos), std::end(Foos));			/* new variable*/
	test_foos_vec(&vec);
	int arr[5] = {0,0,0,0,0};
	for (int __idx=0; __idx<10; __idx++) { /*loop over fixed array*/
	int i = garr[__idx];
		std::cout << i << std::endl;
		if (!(( i == 0 ))) {throw std::runtime_error("assertion failed: ( i == 0 )"); }
	}
	std::cout << std::string("global array iter ok") << std::endl;
	for (int __idx=0; __idx<5; __idx++) { /*loop over fixed array*/
	int i = arr[__idx];
		std::cout << i << std::endl;
		if (!(( i == 0 ))) {throw std::runtime_error("assertion failed: ( i == 0 )"); }
	}
	std::cout << std::string("local array iter ok") << std::endl;
	auto j = 0;  /* auto-fallback <_ast.Num object at 0x7f7447e6a550> */
	for (auto &i: grange) { /*loop over stack vector*/
		std::cout << i << std::endl;
		if (!(( i == j ))) {throw std::runtime_error("assertion failed: ( i == j )"); }
		j ++;
	}
	std::cout << std::string("loop over global range ok") << std::endl;
	for (int __idx=0; __idx<10; __idx++) { /*loop over fixed array*/
	Foo f = Foos[__idx];
		if (!(( f == nullptr ))) {throw std::runtime_error("assertion failed: ( f == nullptr )"); }
	}
	std::cout << std::string("foos initalized to None ok") << std::endl;
	std::vector<Bar> comp; /*comprehension*/
	for (int i=0; i<10; i++) {
		comp.push_back(Bar().__init__(std::string("hello")));
	}
	if (!(( comp.size() == 10 ))) {throw std::runtime_error("assertion failed: ( comp.size() == 10 )"); }
	comp.push_back(Bar().__init__(std::string("world")));
	if (!(( comp.size() == 11 ))) {throw std::runtime_error("assertion failed: ( comp.size() == 11 )"); }
	std::vector<Bar>* s = (new std::vector<Bar>({})); /* 1D Array */
	s->push_back(Bar().__init__(std::string("xxx")));
	if (!(( s->size() == 1 ))) {throw std::runtime_error("assertion failed: ( s->size() == 1 )"); }
	/* arrays:
		bars : ('Bar', '4')
		comp : Bar
		arr : ('int', '5')
		grange : int
		s : Bar
		garr : ('int', '10')
		Foos : ('Foo', '10')
*/
}
	Sub Sub::__init__(Bar arr2[4]) {

		
		(*this).arr2[0] = arr2[0];
(*this).arr2[1] = arr2[1];
(*this).arr2[2] = arr2[2];
(*this).arr2[3] = arr2[3];
		return *this;
		/* arrays:
			grange : int
			garr : ('int', '10')
			arr2 : ('Bar', '4')
			Foos : ('Foo', '10')
*/
	}
	Foo Foo::__init__(bool ok) {

		
		(*this).ok = ok;
		/* arr1 : [4]Bar */;
		return *this;
		/* arrays:
			grange : int
			garr : ('int', '10')
			Foos : ('Foo', '10')
*/
	}
	Bar Bar::__init__(std::string value) {

		
		(*this).value = value;
		return *this;
		/* arrays:
			grange : int
			garr : ('int', '10')
			Foos : ('Foo', '10')
*/
	}
int main() {

	
	auto j = 0;  /* auto-fallback <_ast.Num object at 0x7f7447e73a10> */
	for (auto &i: grange) { /*loop over stack vector*/
		std::cout << i << std::endl;
		if (!(( i == j ))) {throw std::runtime_error("assertion failed: ( i == j )"); }
		j ++;
	}
	stack_test();
	return 0;
	/* arrays:
		grange : int
		garr : ('int', '10')
		Foos : ('Foo', '10')
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
	assert 5 in a
	assert 100 not in a
	assert a.at(4)==5

	a1,a2,a3,a4,a5 = a
	assert a1==1
	assert a2==2
	assert a3==3
	assert a4==4
	assert a5==5

	#print('len a:', len(a))
	assert len(a)==5
	b = a.pop()
	#print('len a after pop:', len(a))
	assert len(a)==4
	assert b==5

	#b = a[len(a)-1]
	a.pop()
	#print('len a:', len(a))
	assert len(a)==3
	#print(b)
	a.insert(0, 1000)
	#a.insert(a.begin(), 1000)

	#print('len a:', len(a))
	#print(a[0])
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
		a1,a2,a3,a4,a5 = arr
		assert a1==1
		assert a2==2
		assert a3==3
		assert a4==4
		assert a5==5

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

auto somefunc() {

	
	std::shared_ptr<std::vector<int>> a( (new std::vector<int>({1,2,3,4,5})) ); /* 1D Array */
	if (!(( (std::find(a->begin(), a->end(), 5) != a->end()) ))) {throw std::runtime_error("assertion failed: ( (std::find(a->begin(), a->end(), 5) != a->end()) )"); }
	if (!(! (( (std::find(a->begin(), a->end(), 100) != a->end()) )))) {throw std::runtime_error("assertion failed: ! (( (std::find(a->begin(), a->end(), 100) != a->end()) ))"); }
	if (!(( a->at(4) == 5 ))) {throw std::runtime_error("assertion failed: ( a->at(4) == 5 )"); }
	auto a1 = (*a)[0];  /* auto-fallback <_ast.Subscript object at 0x7fc59b677d10> */
	auto a2 = (*a)[1];  /* auto-fallback <_ast.Subscript object at 0x7fc59b677e90> */
	auto a3 = (*a)[2];  /* auto-fallback <_ast.Subscript object at 0x7fc59b61d050> */
	auto a4 = (*a)[3];  /* auto-fallback <_ast.Subscript object at 0x7fc59b61d1d0> */
	auto a5 = (*a)[4];  /* auto-fallback <_ast.Subscript object at 0x7fc59b61d350> */
	if (!(( a1 == 1 ))) {throw std::runtime_error("assertion failed: ( a1 == 1 )"); }
	if (!(( a2 == 2 ))) {throw std::runtime_error("assertion failed: ( a2 == 2 )"); }
	if (!(( a3 == 3 ))) {throw std::runtime_error("assertion failed: ( a3 == 3 )"); }
	if (!(( a4 == 4 ))) {throw std::runtime_error("assertion failed: ( a4 == 4 )"); }
	if (!(( a5 == 5 ))) {throw std::runtime_error("assertion failed: ( a5 == 5 )"); }
	if (!(( a->size() == 5 ))) {throw std::runtime_error("assertion failed: ( a->size() == 5 )"); }
	auto b = (*a)[ a->size()-1 ];
a->pop_back();
	if (!(( a->size() == 4 ))) {throw std::runtime_error("assertion failed: ( a->size() == 4 )"); }
	if (!(( b == 5 ))) {throw std::runtime_error("assertion failed: ( b == 5 )"); }
	a->pop_back();
	if (!(( a->size() == 3 ))) {throw std::runtime_error("assertion failed: ( a->size() == 3 )"); }
	a->insert(a->begin()+0, 1000);
	if (!(( (*a)[0] == 1000 ))) {throw std::runtime_error("assertion failed: ( (*a)[0] == 1000 )"); }
	if (!(( a->size() == 4 ))) {throw std::runtime_error("assertion failed: ( a->size() == 4 )"); }
	auto c = (*a)[0];
a->erase(a->begin(),a->begin()+1);
	if (!(( c == 1000 ))) {throw std::runtime_error("assertion failed: ( c == 1000 )"); }
	if (!(( a->size() == 3 ))) {throw std::runtime_error("assertion failed: ( a->size() == 3 )"); }
	std::cout << std::string("testing insert empty array") << std::endl;
	std::shared_ptr<std::vector<int>> empty( (new std::vector<int>({10,20})) ); /* 1D Array */
	a->insert((a->begin() + 1), empty->begin(), empty->end());
	for (auto &val: (*a)) { /*loop over heap vector*/
		std::cout << val << std::endl;
	}
	/* arrays:
		a : int
		empty : int
*/
}
auto stackfunc() {

	
		int arr[5] = {1,2,3,4,5};
	std::cout << std::string("sizeof arr:");
std::cout << sizeof(arr);std::cout << std::endl;
	auto a1 = arr[0];  /* auto-fallback <_ast.Subscript object at 0x7fc59b612c10> */
	auto a2 = arr[1];  /* auto-fallback <_ast.Subscript object at 0x7fc59b612d90> */
	auto a3 = arr[2];  /* auto-fallback <_ast.Subscript object at 0x7fc59b612f10> */
	auto a4 = arr[3];  /* auto-fallback <_ast.Subscript object at 0x7fc59b6130d0> */
	auto a5 = arr[4];  /* auto-fallback <_ast.Subscript object at 0x7fc59b613250> */
	if (!(( a1 == 1 ))) {throw std::runtime_error("assertion failed: ( a1 == 1 )"); }
	if (!(( a2 == 2 ))) {throw std::runtime_error("assertion failed: ( a2 == 2 )"); }
	if (!(( a3 == 3 ))) {throw std::runtime_error("assertion failed: ( a3 == 3 )"); }
	if (!(( a4 == 4 ))) {throw std::runtime_error("assertion failed: ( a4 == 4 )"); }
	if (!(( a5 == 5 ))) {throw std::runtime_error("assertion failed: ( a5 == 5 )"); }
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
	auto k = 2;  /* auto-fallback <_ast.Num object at 0x7fc59b638350> */
	/* <fixed size slice> k : None : -1 */
	int s[5-k];
	int __L = 0;
	for (int __i=5-1; __i>=k; __i--) {
	  s[__L] = arr2[__i];
	  __L ++;
	}
	for (int __idx=0; __idx<5-k; __idx++) { /*loop over fixed array*/
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
	for (int __idx=0; __idx<4; __idx++) { /*loop over fixed array*/
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	A* __init__(int x);
	int method1();
	std::string getname();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x']
	B* __init__(int x);
	int method1();
	auto method2(int y);
	std::string getname();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true; __classid__=2;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x']
	C* __init__(int x);
	int method1();
	auto say_hi();
	std::string getname();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true; __classid__=1;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return this->__class__;}
};
int my_generic(std::shared_ptr<A> g) {

	
	return g->method1();
}
	std::string C::getname() {

		
		return this->__class__;
	}
	auto C::say_hi() {

		
		std::cout << std::string("hi from C") << std::endl;
	}
	int C::method1() {

		
		return (this->x + 200);
	}
	C* C::__init__(int x) {

		
		this->x = x;
		return this;
	}
	std::string B::getname() {

		
		return this->__class__;
	}
	auto B::method2(int y) {

		
		std::cout << (this->x + y) << std::endl;
	}
	int B::method1() {

		
		return (this->x * 2);
	}
	B* B::__init__(int x) {

		
		this->x = x;
		return this;
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

	
	auto a = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(1); return _;}();			/* new variable*/
	auto b = [&](){auto _ = std::shared_ptr<B>(new B()); _->__init__(200); return _;}();			/* new variable*/
	auto c = [&](){auto _ = std::shared_ptr<C>(new C()); _->__init__(3000); return _;}();			/* new variable*/
	std::cout << a->__class__ << std::endl;
	std::cout << b->__class__ << std::endl;
	std::cout << c->__class__ << std::endl;
	std::cout << std::string("- - - - - - -") << std::endl;
	std::shared_ptr<std::vector<std::shared_ptr<A>>> arr( ( new std::vector<std::shared_ptr<A>>({a,b,c}) ) ); /* 1D Array */
	for (auto &item: (*arr)) { /*loop over heap vector*/
		std::cout << item->__class__ << std::endl;
		std::cout << my_generic(item) << std::endl;
	}
	std::cout << std::string("- - - - - - -") << std::endl;
	for (auto &item: (*arr)) { /*loop over heap vector*/
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
* [block_scope.py](c++/block_scope.py)

input:
------
```python
'''
variable block scope
http://stackoverflow.com/questions/6167923/block-scope-in-python
'''

def main():
	for x in range(3):
		print x
		y = x

	## below is valid in python, but not in pythia.
	#assert x==2
	#assert y==x

	## note because `y` above is block scoped inside the for loop,
	## the type of `y` can be changed here.
	y = 'hi'
	print y

	print 'OK'
```
output:
------
```c++

int main() {

	
	for (int x=0; x<3; x++) {
		std::cout << x << std::endl;
		auto y = x;  /* auto-fallback <_ast.Name object at 0x7fd6cbe1f550> */
	}
	auto y = std::string("hi");  /* auto-fallback <_ast.Str object at 0x7fd6cbe1f610> */
	std::cout << y << std::endl;
	std::cout << std::string("OK") << std::endl;
	return 0;
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
	auto index = 0;  /* auto-fallback <_ast.Num object at 0x7fcf1bdf7650> */
	(*a)[index] = 100;
	std::cout << (*a)[index] << std::endl;
	auto s = std::string("hello world");  /* auto-fallback <_ast.Str object at 0x7fcf1bdf79d0> */
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
	def __init__(self, x:int, other:A):
		self.x = x
		self.other = other
	def method(self) -> int:
		return self.x
	def get_self(self) ->self:
		return self
	def set_self(self):
		#self.other.other = self  ## TODO
		self.other.other = self.get_self()

class B(A):
	def foo(self) ->int:
		return self.x * 2
	def foo(self, x:float, y:float) ->int:
		return (x+y) as int

class C(A):
	def bar(self) ->int:
		return self.x + 200

class D(C):
	def hey(self) ->int:
		return self.x + 1


def some_subclass( x:int, o:A ) ->A:
	switch x:
		case 0:
			a = A(1,o)
			return a
		case 1:
			b = B(2,o)
			return b
		case 2:
			c = C(3,o)
			return c
		case 3:
			d = D(4,o)
			return d


def main():
	a = some_subclass(0, None)
	b = some_subclass(1, a)
	c = some_subclass(2, b)
	d = some_subclass(3, c)

	bb = b.get_self()
	#assert bb.foo()==4  ## this wont work here

	#assert a.getclassname() == 'A'  ## TODO fix
	#assert b.getclassname() == 'B'
	print(c.getclassname())
	print(d.getclassname())

	assert a.method() == a.x
	assert a.x == 1
	assert b.method() == b.x
	assert b.x == 2

	#assert d.hey()==5  ## not allowed before `if isinstance(d,D)`
	assert b.other.method() == 1
	assert c.other.method() == b.x

	## the method not allowed here because `other` is reduced to the super class `A`
	#assert c.other.foo()==4
	## this works using an explicit cast
	assert (c.other as B).foo()==4
	## testing overloaded method
	assert (c.other as B).foo(
			100 as float,
			200 as float
		) == 300



	print('- - - - - - - ')
	if isinstance(b, B):
		assert b.foo()==4
		bbb = b.get_self()
		assert bbb.foo()==4
	else:
		raise RuntimeError('error: b is not type B')

	if isinstance(c, C):
		assert c.method()==3
		assert c.bar()==203
		## not allowed here either, because `foo` is not a method of the base class `A`
		#assert c.other.foo()==4
		if isinstance(c.other, B):
			assert c.other.foo()==4

	else:
		print('error: c is not type C')

	if isinstance(d, D):
		print('d is type D')
		#print(d.bar())  ## TODO, subclass from C.
		assert d.hey()==5
	else:
		print('error: d is not type D')

	print('------------------')
	for i in range(3):
		o = some_subclass(i, a)
		print(o.method())
		if isinstance(o, B):
			print(o.foo())
		if isinstance(o,C):		## TODO-FIX elif isinstance(o,C)
			print(o.bar())

		switch type(o):
			case B:
				assert o.foo()==4
			case C:
				assert o.bar()==203

	print('end of test')
```
output:
------
```c++

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	std::shared_ptr<A>  other;
	A* __init__(int x, std::shared_ptr<A> other);
	int method();
	std::shared_ptr<A> get_self();
	auto set_self();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
class B:  public A {
  public:
//	members from class: A  ['x', 'other']
	B* __init__(int x, std::shared_ptr<A> other);
	int foo();
	int foo(float x, float y);
	int method();
	std::shared_ptr<B> get_self();
	auto set_self();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	B() {__class__ = std::string("B"); __initialized__ = true; __classid__=2;}
	B(bool init) {__class__ = std::string("B"); __initialized__ = init; __classid__=2;}
	std::string getclassname() {return this->__class__;}
};
class C:  public A {
  public:
//	members from class: A  ['x', 'other']
	C* __init__(int x, std::shared_ptr<A> other);
	int bar();
	int method();
	std::shared_ptr<C> get_self();
	auto set_self();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	C() {__class__ = std::string("C"); __initialized__ = true; __classid__=1;}
	C(bool init) {__class__ = std::string("C"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return this->__class__;}
};
class D:  public C {
  public:
//	members from class: A  ['x', 'other']
	D* __init__(int x, std::shared_ptr<A> other);
	int hey();
	int bar();
	int method();
	std::shared_ptr<D> get_self();
	auto set_self();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	D() {__class__ = std::string("D"); __initialized__ = true; __classid__=3;}
	D(bool init) {__class__ = std::string("D"); __initialized__ = init; __classid__=3;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<A> some_subclass(int x, std::shared_ptr<A> o) {

	
		switch (x) {
		case 0: {
	auto a = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(1, o); return _;}();			/* new variable*/
	return a;
	} break;
		case 1: {
	auto b = [&](){auto _ = std::shared_ptr<B>(new B()); _->__init__(2, o); return _;}();			/* new variable*/
	return b;
	} break;
		case 2: {
	auto c = [&](){auto _ = std::shared_ptr<C>(new C()); _->__init__(3, o); return _;}();			/* new variable*/
	return c;
	} break;
		case 3: {
	auto d = [&](){auto _ = std::shared_ptr<D>(new D()); _->__init__(4, o); return _;}();			/* new variable*/
	return d;
	} break;
	}
}
	auto D::set_self() {

		
		this->other->other = this->get_self();
	}
	std::shared_ptr<D> D::get_self() {

		
		return std::static_pointer_cast<D>(shared_from_this());
	}
	int D::method() {

		
		return this->x;
	}
	int D::bar() {

		
		return (this->x + 200);
	}
	int D::hey() {

		
		return (this->x + 1);
	}
	D* D::__init__(int x, std::shared_ptr<A> other) {

		
		this->x = x;
		this->other = other;
		return this;
	}
	auto C::set_self() {

		
		this->other->other = this->get_self();
	}
	std::shared_ptr<C> C::get_self() {

		
		return std::static_pointer_cast<C>(shared_from_this());
	}
	int C::method() {

		
		return this->x;
	}
	int C::bar() {

		
		return (this->x + 200);
	}
	C* C::__init__(int x, std::shared_ptr<A> other) {

		
		this->x = x;
		this->other = other;
		return this;
	}
	auto B::set_self() {

		
		this->other->other = this->get_self();
	}
	std::shared_ptr<B> B::get_self() {

		
		return std::static_pointer_cast<B>(shared_from_this());
	}
	int B::method() {

		
		return this->x;
	}
	int B::foo(float x, float y) {

		
		return static_cast<int>((x + y));
	}
	int B::foo() {

		
		return (this->x * 2);
	}
	B* B::__init__(int x, std::shared_ptr<A> other) {

		
		this->x = x;
		this->other = other;
		return this;
	}
	auto A::set_self() {

		
		this->other->other = this->get_self();
	}
	std::shared_ptr<A> A::get_self() {

		
		return std::static_pointer_cast<A>(shared_from_this());
	}
	int A::method() {

		
		return this->x;
	}
	A* A::__init__(int x, std::shared_ptr<A> other) {

		
		this->x = x;
		this->other = other;
		return this;
	}
int main() {

	
	auto a = some_subclass(0, nullptr);			/* new variable*/
	auto b = some_subclass(1, a);			/* new variable*/
	auto c = some_subclass(2, b);			/* new variable*/
	auto d = some_subclass(3, c);			/* new variable*/
	auto bb = b->get_self();			/* b   */
	std::cout << c->getclassname() << std::endl;
	std::cout << d->getclassname() << std::endl;
	if (!(( a->method() == a->x ))) {throw std::runtime_error("assertion failed: ( a->method() == a->x )"); }
	if (!(( a->x == 1 ))) {throw std::runtime_error("assertion failed: ( a->x == 1 )"); }
	if (!(( b->method() == b->x ))) {throw std::runtime_error("assertion failed: ( b->method() == b->x )"); }
	if (!(( b->x == 2 ))) {throw std::runtime_error("assertion failed: ( b->x == 2 )"); }
	if (!(( b->other->method() == 1 ))) {throw std::runtime_error("assertion failed: ( b->other->method() == 1 )"); }
	if (!(( c->other->method() == b->x ))) {throw std::runtime_error("assertion failed: ( c->other->method() == b->x )"); }
	if (!(( std::static_pointer_cast<B>(c->other)->foo() == 4 ))) {throw std::runtime_error("assertion failed: ( std::static_pointer_cast<B>(c->other)->foo() == 4 )"); }
	if (!(( std::static_pointer_cast<B>(c->other)->foo(static_cast<float>(100), static_cast<float>(200)) == 300 ))) {throw std::runtime_error("assertion failed: ( std::static_pointer_cast<B>(c->other)->foo(static_cast<float>(100), static_cast<float>(200)) == 300 )"); }
	std::cout << std::string("- - - - - - - ") << std::endl;
	if ((b->__class__==std::string("B"))) {
		auto _cast_b = std::static_pointer_cast<B>(b);
		if (!(( _cast_b->foo() == 4 ))) {throw std::runtime_error("assertion failed: ( _cast_b->foo() == 4 )"); }
		auto bbb = _cast_b->get_self();			/* b   */
		if (!(( bbb->foo() == 4 ))) {throw std::runtime_error("assertion failed: ( bbb->foo() == 4 )"); }
	} else {
		throw RuntimeError(std::string("error: b is not type B"));
	}
	if ((c->__class__==std::string("C"))) {
		auto _cast_c = std::static_pointer_cast<C>(c);
		if (!(( _cast_c->method() == 3 ))) {throw std::runtime_error("assertion failed: ( _cast_c->method() == 3 )"); }
		if (!(( _cast_c->bar() == 203 ))) {throw std::runtime_error("assertion failed: ( _cast_c->bar() == 203 )"); }
		if ((_cast_c->other->__class__==std::string("B"))) {
			auto _cast__cast_c_other = std::static_pointer_cast<B>(_cast_c->other);
			if (!(( _cast__cast_c_other->foo() == 4 ))) {throw std::runtime_error("assertion failed: ( _cast__cast_c_other->foo() == 4 )"); }
		}
	} else {
		std::cout << std::string("error: c is not type C") << std::endl;
	}
	if ((d->__class__==std::string("D"))) {
		auto _cast_d = std::static_pointer_cast<D>(d);
		std::cout << std::string("d is type D") << std::endl;
		if (!(( _cast_d->hey() == 5 ))) {throw std::runtime_error("assertion failed: ( _cast_d->hey() == 5 )"); }
	} else {
		std::cout << std::string("error: d is not type D") << std::endl;
	}
	std::cout << std::string("------------------") << std::endl;
	for (int i=0; i<3; i++) {
		auto o = some_subclass(i, a);			/* new variable*/
		std::cout << o->method() << std::endl;
		if ((o->__class__==std::string("B"))) {
			auto _cast_o = std::static_pointer_cast<B>(o);
			std::cout << _cast_o->foo() << std::endl;
		}
		if ((o->__class__==std::string("C"))) {
			auto _cast_o = std::static_pointer_cast<C>(o);
			std::cout << _cast_o->bar() << std::endl;
		}
				switch (o->__classid__) {
				case 2: {
			auto _cast_o = std::static_pointer_cast<B>(o);
		if (!(( _cast_o->foo() == 4 ))) {throw std::runtime_error("assertion failed: ( _cast_o->foo() == 4 )"); }
		} break;
				case 1: {
			auto _cast_o = std::static_pointer_cast<C>(o);
		if (!(( _cast_o->bar() == 203 ))) {throw std::runtime_error("assertion failed: ( _cast_o->bar() == 203 )"); }
		} break;
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  x;
	A* __init__(int x);
	~A();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
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

	
	auto a = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(1); return _;}();			/* new variable*/
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
			print 'a is not None'
			a = None
			assert a is None

		let b:A = None
		print b.is_initialized()
		if b is None:
			print 'b is acting like a nullptr'

		assert b.is_initialized() is False
		c = A()
		## test that ensures `a` can be restored from nullptr back to an object.
		a = c

def main():
	test()
```
output:
------
```c++

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	A __init__();
	bool is_initialized();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return __class__;}
};
auto test() {

	
	auto a = A().__init__();			/* new variable*/
	std::cout << a.is_initialized() << std::endl;
	if (!(a.is_initialized())) {throw std::runtime_error("assertion failed: a.is_initialized()"); }
	if (( a != nullptr )) {
		std::cout << std::string("a is not None") << std::endl;
		a = nullptr;
		if (!(( a == nullptr ))) {throw std::runtime_error("assertion failed: ( a == nullptr )"); }
	}
	A  b = A(false);
	std::cout << b.is_initialized() << std::endl;
	if (( b == nullptr )) {
		std::cout << std::string("b is acting like a nullptr") << std::endl;
	}
	if (!(( b.is_initialized() == false ))) {throw std::runtime_error("assertion failed: ( b.is_initialized() == false )"); }
	auto c = A().__init__();			/* new variable*/
	a = c;
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
* [tuple_types.py](c++/tuple_types.py)

input:
------
```python
'''
std::tuple<Type1, Type2, etc...>
'''
with typedef:
	HeapTArray = []tuple( []f64, []f64, f64 )
	HeapTupleType = tuple( []f64, []f64, f64 )
	HeapArrayOfTuples = []HeapTupleType()
	HTupleOfTuples    = tuple( HeapTupleType, HeapTupleType )
	HTTArray = []HTupleOfTuples()

## IDX needs to be a constant so std::get<IDX> can be resolved at compile time.
with constant: IDX = 0

def test_typedefs():

	x = HeapTArray()
	a = [1.1,2.2,3.3]
	b = [0.1,0.2]
	x.push_back(
		(a, b, 0.99)
	)
	print x
	assert len(x)==1

	x.push_back( ([0.1, 0.2], [0.9, 0.8], 0.1) )
	assert len(x)==2

	c = ([0.1, 0.2], [0.9, 0.8], 0.1)
	x.push_back( c )

	assert len(x)==3

	y = HeapTArray([
		(a, b, 0.99),
		(b, a, 0.5)
	])

	tt = HTupleOfTuples( (a, b, 0.99), (b, c, 0.11) )
	htta = HTTArray([tt])
	assert len(htta)==1
	#htta = HTTArray()
	htta.push_back( tt )
	assert len(htta)==2

	## TODO fixme, bug with typedef's and nested tuples?
	#htta2 = HTTArray()
	#assert len(htta2)==0
	#htta2.push_back( tt )
	#assert len(htta2)==1
	#htta2.push_back(
	#	( (a, b, 0.99), (b, c, 0.11) )
	#)
	#htta2.push_back( tt )

with stack:
	with typedef:
		StackTArray = []tuple( []f64, []f64, f64 )

	def test_stack_array( arr: StackTArray ):
		print 'len of arr:', len(arr)

	def test_array_of_nested_tuples_stack(n:int):
		with typedef: T = tuple(f64,f64)
		r = []tuple( T, T )
		for i in range(n):
			a = (1.1, 1.2)
			b = (2.2, 2.3)
			r.append( (a,b) )
			#c = (a,b)
			#r.append( c )
		return r


	def test_stack():
		print 'stack test'
		tuplearray = []tuple( []f64, []f64, f64 )
		a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
		b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
		tuplearray.append( a )
		tuplearray.append( b )
		test_stack_array( tuplearray )

		with get as "std::get<%s>(%s)":
			for item in tuplearray:
				vec3 = get(0, item)
				vec2 = get(1, item)
				num  = get(2, item)
				print vec3[0], vec3[1], vec3[2]

				v3 = item[{ IDX }]
				assert v3[0]==vec3[0]

				v4 = tuple.get(item, 0)
				assert v4[0]==v3[0]

		tu = test_array_of_nested_tuples_stack(6)
		assert len(tu)


def test_heap_array( arr: HeapTArray ):
	print 'len of arr:', len(arr)

def test_returns_array_of_tuples(n) -> []tuple(f64, f64):
	r = []tuple( f64, f64 )
	for i in range(n):
		t = (1.1, 1.2)
		r.append(t)
	return r

## note: g++4.9 can not guess a complex return type, when the parameter `n` is untyped, 
## so `n:int` is required so the return type can automatically be deduced by g++.
def test_array_of_nested_tuples(n:int):
	with typedef: T = tuple(f64,f64)
	r = []tuple( T, T )

	for i in range(n):
		a = (1.1, 1.2)
		b = (2.2, 2.3)
		r.append( (a,b) )
		#c = (a,b)
		#r.append( c )
	return r



def test_heap():
	print 'heap test'
	nested = test_array_of_nested_tuples(4)
	assert len(nested)==4

	tarr = test_returns_array_of_tuples(3)
	assert len(tarr)==3

	tuplearray = []tuple( []f64, []f64, f64 )
	a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
	b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
	tuplearray.append( a )
	tuplearray.append( b )

	test_heap_array( tuplearray )

	print a[{0}][1]
	with constant:
		index = 2

	#b[{index}] = 40.4  ## not allowed
	print b[{index}]

	for item in tuplearray:
		with get as "std::get<%s>(*%s)":
			vec3 = get(0, item)
			vec2 = get(1, item)
			num  = get(2, item)
		print vec3[0], vec3[1], vec3[2]

		v3 = item[{ 0 }]
		assert v3[0]==vec3[0]

		v4 = tuple.get(item, 0)
		assert v4[0]==v3[0]

def main():
	test_stack()
	test_heap()
```
output:
------
```c++

typedef std::shared_ptr< std::vector<std::shared_ptr<std::tuple<std::shared_ptr<std::vector<f64>>,std::shared_ptr<std::vector<f64>>,f64>>> > HeapTArray;
typedef std::shared_ptr<std::tuple<std::shared_ptr<std::vector<f64>>,std::shared_ptr<std::vector<f64>>,f64>> HeapTupleType;
typedef std::shared_ptr<std::vector<HeapTupleType>> HeapArrayOfTuples;
typedef std::shared_ptr<std::tuple<HeapTupleType,HeapTupleType>> HTupleOfTuples;
typedef std::shared_ptr<std::vector<HTupleOfTuples>> HTTArray;
const int IDX = 0;
auto test_typedefs() {

	
	auto x = /*typedef-tuple-array:std::vector<tuple>*/HeapTArray();			/* new variable*/
	std::shared_ptr<std::vector<float64>> a( (new std::vector<float64>({1.1,2.2,3.3})) ); /* 1D Array */
	std::shared_ptr<std::vector<float64>> b( (new std::vector<float64>({0.1,0.2})) ); /* 1D Array */
	x->push_back(std::make_shared<std::tuple<decltype(a),decltype(b),float64>>(std::make_tuple(a,b,0.99)));
	std::cout << x << std::endl;
	if (!(( x->size() == 1 ))) {throw std::runtime_error("assertion failed: ( x->size() == 1 )"); }
	x->push_back(std::make_shared<std::tuple<std::shared_ptr<std::vector<float64>>,std::shared_ptr<std::vector<float64>>,float64>>(std::make_tuple(std::shared_ptr<std::vector<float64>>(new std::vector<float64>{0.1,0.2}),std::shared_ptr<std::vector<float64>>(new std::vector<float64>{0.9,0.8}),0.1)));
	if (!(( x->size() == 2 ))) {throw std::runtime_error("assertion failed: ( x->size() == 2 )"); }
	auto c = std::make_shared<std::tuple<std::shared_ptr<std::vector<float64>>,std::shared_ptr<std::vector<float64>>,float64>>(std::make_tuple(std::shared_ptr<std::vector<float64>>(new std::vector<float64>{0.1,0.2}),std::shared_ptr<std::vector<float64>>(new std::vector<float64>{0.9,0.8}),0.1)); /*new-tuple*/
	x->push_back(c);
	if (!(( x->size() == 3 ))) {throw std::runtime_error("assertion failed: ( x->size() == 3 )"); }
	auto y = /*typedef: std::vector<tuple>*/std::make_shared<std::vector<std::shared_ptr<std::tuple<decltype(a),decltype(b),float64>>>>(std::vector<std::shared_ptr<std::tuple<decltype(a),decltype(b),float64>>>{std::make_shared<std::tuple<decltype(a),decltype(b),float64>>(std::make_tuple(a,b,0.99)),std::make_shared<std::tuple<decltype(b),decltype(a),float64>>(std::make_tuple(b,a,0.5))});			/* new variable*/
	auto tt = /*typedef: tuple(HeapTupleType, HeapTupleType)*/[&](){auto _ = std::make_tuple(std::make_shared<std::tuple<decltype(a),decltype(b),float64>>(std::make_tuple(a,b,0.99)),std::make_shared<std::tuple<decltype(b),decltype(c),float64>>(std::make_tuple(b,c,0.11))); return std::make_shared<decltype(_)>(_);}();			/* new variable*/
	auto htta = /*typedef: std::vector<HTupleOfTuples>*/std::make_shared<std::vector<decltype(tt)>>(std::vector<decltype(tt)>{tt});			/* new variable*/
	if (!(( htta->size() == 1 ))) {throw std::runtime_error("assertion failed: ( htta->size() == 1 )"); }
	htta->push_back(tt);
	if (!(( htta->size() == 2 ))) {throw std::runtime_error("assertion failed: ( htta->size() == 2 )"); }
	/* arrays:
		a : float64
		b : float64
*/
}
typedef std::vector<std::tuple<std::vector<f64>,std::vector<f64>,f64>> StackTArray;
auto test_stack_array(StackTArray arr) {

	
	std::cout << std::string("len of arr:");
std::cout << arr.size();std::cout << std::endl;
}
auto test_array_of_nested_tuples_stack(int n) {

	
	typedef std::tuple<f64,f64> T;
	auto r = std::vector<std::tuple<T,T>>();
	for (int i=0; i<n; i++) {
		auto a = std::make_tuple(1.1,1.2); /*new-tuple*/
		auto b = std::make_tuple(2.2,2.3); /*new-tuple*/
		r.push_back(std::make_tuple(a,b));
	}
	return r;
	/* arrays:
		r : tuple
*/
}
auto test_stack() {

	
	std::cout << std::string("stack test") << std::endl;
	auto tuplearray = std::vector<std::tuple<std::vector<f64>,std::vector<f64>,f64>>();
	auto a = std::make_tuple(std::vector<float64>{1.1,2.2,3.3},std::vector<float64>{4.4,5.5},100.0); /*new-tuple*/
	auto b = std::make_tuple(std::vector<float64>{6.1,7.2,8.3},std::vector<float64>{9.4,0.5},1.0); /*new-tuple*/
	tuplearray.push_back(a);
	tuplearray.push_back(b);
	test_stack_array(tuplearray);
	for (auto &item: tuplearray) { /*loop over stack vector*/
		auto vec3 = std::get<0>(item);			/* new variable*/
		auto vec2 = std::get<1>(item);			/* new variable*/
		auto num = std::get<2>(item);			/* new variable*/
		std::cout << vec3[0];
std::cout << vec3[1];
std::cout << vec3[2];std::cout << std::endl;
		auto v3 = std::get<IDX>(item);  /* auto-fallback <_ast.Subscript object at 0x7f2f0141d950> */
		if (!(( v3[0] == vec3[0] ))) {throw std::runtime_error("assertion failed: ( v3[0] == vec3[0] )"); }
		auto v4 = std::get<0>(item);			/* tuple   */
		if (!(( v4[0] == v3[0] ))) {throw std::runtime_error("assertion failed: ( v4[0] == v3[0] )"); }
	}
	auto tu = test_array_of_nested_tuples_stack(6);			/* new variable*/
	if (!(tu.size())) {throw std::runtime_error("assertion failed: tu.size()"); }
	/* arrays:
		tuplearray : tuple
*/
}
auto test_heap_array(HeapTArray arr) {

	
	std::cout << std::string("len of arr:");
std::cout << arr->size();std::cout << std::endl;
}
std::shared_ptr<std::vector<std::shared_ptr<std::tuple<f64, f64>>>> test_returns_array_of_tuples(auto n) {

	
	auto r = std::make_shared<std::vector< std::shared_ptr<std::tuple<f64,f64>> >>(std::vector< std::shared_ptr<std::tuple<f64,f64>> >());
	for (int i=0; i<n; i++) {
		auto t = std::make_shared<std::tuple<float64,float64>>(std::make_tuple(1.1,1.2)); /*new-tuple*/
		r->push_back(t);
	}
	return r;
	/* arrays:
		r : tuple
*/
}
auto test_array_of_nested_tuples(int n) {

	
	typedef std::shared_ptr<std::tuple<f64,f64>> T;
	auto r = std::make_shared<std::vector< std::shared_ptr<std::tuple<T,T>> >>(std::vector< std::shared_ptr<std::tuple<T,T>> >());
	for (int i=0; i<n; i++) {
		auto a = std::make_shared<std::tuple<float64,float64>>(std::make_tuple(1.1,1.2)); /*new-tuple*/
		auto b = std::make_shared<std::tuple<float64,float64>>(std::make_tuple(2.2,2.3)); /*new-tuple*/
		r->push_back(std::make_shared<std::tuple<decltype(a),decltype(b)>>(std::make_tuple(a,b)));
	}
	return r;
	/* arrays:
		r : tuple
*/
}
auto test_heap() {

	
	std::cout << std::string("heap test") << std::endl;
	auto nested = test_array_of_nested_tuples(4);			/* new variable*/
	if (!(( nested->size() == 4 ))) {throw std::runtime_error("assertion failed: ( nested->size() == 4 )"); }
	auto tarr = test_returns_array_of_tuples(3);			/* new variable*/
	if (!(( tarr->size() == 3 ))) {throw std::runtime_error("assertion failed: ( tarr->size() == 3 )"); }
	auto tuplearray = std::make_shared<std::vector< std::shared_ptr<std::tuple<std::shared_ptr<std::vector<f64>>,std::shared_ptr<std::vector<f64>>,f64>> >>(std::vector< std::shared_ptr<std::tuple<std::shared_ptr<std::vector<f64>>,std::shared_ptr<std::vector<f64>>,f64>> >());
	auto a = std::make_shared<std::tuple<std::shared_ptr<std::vector<float64>>,std::shared_ptr<std::vector<float64>>,float64>>(std::make_tuple(std::shared_ptr<std::vector<float64>>(new std::vector<float64>{1.1,2.2,3.3}),std::shared_ptr<std::vector<float64>>(new std::vector<float64>{4.4,5.5}),100.0)); /*new-tuple*/
	auto b = std::make_shared<std::tuple<std::shared_ptr<std::vector<float64>>,std::shared_ptr<std::vector<float64>>,float64>>(std::make_tuple(std::shared_ptr<std::vector<float64>>(new std::vector<float64>{6.1,7.2,8.3}),std::shared_ptr<std::vector<float64>>(new std::vector<float64>{9.4,0.5}),1.0)); /*new-tuple*/
	tuplearray->push_back(a);
	tuplearray->push_back(b);
	test_heap_array(tuplearray);
	std::cout << (*std::get<0>(*a))[1] << std::endl;
		const auto index = 2;  /* auto-fallback <_ast.Num object at 0x7f2eff2fab50> */
	std::cout << std::get<index>(*b) << std::endl;
	for (auto &item: (*tuplearray)) { /*loop over heap vector*/
		auto vec3 = std::get<0>(*item);			/* new variable*/
		auto vec2 = std::get<1>(*item);			/* new variable*/
		auto num = std::get<2>(*item);			/* new variable*/
		std::cout << (*vec3)[0];
std::cout << (*vec3)[1];
std::cout << (*vec3)[2];std::cout << std::endl;
		auto v3 = std::get<0>(*item);  /* auto-fallback <_ast.Subscript object at 0x7f2eff2fe810> */
		if (!(( (*v3)[0] == (*vec3)[0] ))) {throw std::runtime_error("assertion failed: ( (*v3)[0] == (*vec3)[0] )"); }
		auto v4 = std::get<0>(*item);			/* tuple   */
		if (!(( (*v4)[0] == (*v3)[0] ))) {throw std::runtime_error("assertion failed: ( (*v4)[0] == (*v3)[0] )"); }
	}
	/* arrays:
		tuplearray : tuple
*/
}
int main() {

	
	test_stack();
	test_heap();
	return 0;
}
```
* [map_types.py](c++/map_types.py)

input:
------
```python
'''
std::map<KEY, VALUE>
'''
mymap = {
	'key1' : [1,2,3],
	'key2' : [4,5,6,7]
}

FOO = 1.1
tuplemap = {
	'A': ([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], FOO),
	'B': ([7.0, 8.0, 9.0], [0.0, 0.0, 0.0], FOO*2.2)
}

with stack:
	tuplemap_stack = {
		'A': ([1.0, 2.0, 3.0], [4.0, 5.0, 6.0], FOO),
		'B': ([7.0, 8.0, 9.0], [0.0, 0.0, 0.0], FOO*2.2)
	}

	def test_stack():
		print 'stack test...'
		m1 = {
			'K1' : [0,1],
			'K2' : [2,3]
		}
		assert m1['K1'][0]==0
		assert m1['K1'][1]==1
		assert m1['K2'][0]==2
		assert m1['K2'][1]==3

		vecx = tuple.get( tuplemap_stack['A'], 0 )
		assert vecx[0]==1.0


def test_heap():
	print 'heap test...'
	m1 = {
		'K1' : [0,1],
		'K2' : [2,3]
	}
	assert m1['K1'][0]==0
	assert m1['K1'][1]==1
	assert m1['K2'][0]==2
	assert m1['K2'][1]==3

	with get as 'std::get<%s>(*%s)':
		vec = get(0, tuplemap['A'])
		assert vec[0]==1.0

	vecx = tuple.get( tuplemap['A'], 0 )
	assert vecx[0]==1.0

	print 'testing loop over map keys'
	for key in m1:
		print 'key:', key

	print 'testing loop over map keys and values'
	for (key,val) in m1:
		print 'key:', key
		print 'value:', val

	keys = dict.keys(m1)
	assert len(keys)==2
	for key in keys:
		print key

	assert 'K1' in keys
	assert 'invalid-key' not in keys

	values = dict.values(m1)
	assert len(values)==2


def main():
	print mymap
	assert mymap['key1'][0]==1
	assert mymap['key2'][1]==5
	test_heap()
	test_stack()
	print 'OK'
	
```
output:
------
```c++

auto mymap = std::shared_ptr<std::map<std::string,std::vector<int>*>>(new std::map<std::string,std::vector<int>*>{{std::string("key1"), new std::vector<int>{1,2,3}}
,{std::string("key2"), new std::vector<int>{4,5,6,7}}});
int FOO = 1.1;
auto tuplemap = std::shared_ptr<std::map<std::string,std::shared_ptr<std::tuple<std::vector<double>*,std::vector<double>*,double>>>>(new std::map<std::string,std::shared_ptr<std::tuple<std::vector<double>*,std::vector<double>*,double>>>{{std::string("A"), std::make_shared<std::tuple<std::vector<double>*,std::vector<double>*,double>>(std::make_tuple(new std::vector<float64>{1.0,2.0,3.0},new std::vector<float64>{4.0,5.0,6.0},FOO))}
,{std::string("B"), std::make_shared<std::tuple<std::vector<double>*,std::vector<double>*,double>>(std::make_tuple(new std::vector<float64>{7.0,8.0,9.0},new std::vector<float64>{0.0,0.0,0.0},(FOO * 2.2)))}});
auto tuplemap_stack = std::map<std::string, std::tuple<std::vector<double>,std::vector<double>,double>>{{std::string("A"), std::make_tuple(std::vector<float64>{1.0,2.0,3.0},std::vector<float64>{4.0,5.0,6.0},FOO)}
,{std::string("B"), std::make_tuple(std::vector<float64>{7.0,8.0,9.0},std::vector<float64>{0.0,0.0,0.0},(FOO * 2.2))}};
auto test_stack() {

	
	std::cout << std::string("stack test...") << std::endl;
	auto m1 = std::map<std::string,std::vector<int>>{{std::string("K1"),std::vector<int>{0,1}}
,{std::string("K2"),std::vector<int>{2,3}}};
	if (!(( m1[std::string("K1")][0] == 0 ))) {throw std::runtime_error("assertion failed: ( m1[std::string(\"K1\")][0] == 0 )"); }
	if (!(( m1[std::string("K1")][1] == 1 ))) {throw std::runtime_error("assertion failed: ( m1[std::string(\"K1\")][1] == 1 )"); }
	if (!(( m1[std::string("K2")][0] == 2 ))) {throw std::runtime_error("assertion failed: ( m1[std::string(\"K2\")][0] == 2 )"); }
	if (!(( m1[std::string("K2")][1] == 3 ))) {throw std::runtime_error("assertion failed: ( m1[std::string(\"K2\")][1] == 3 )"); }
	auto vecx = std::get<0>(tuplemap_stack[std::string("A")]);			/* tuple   */
	if (!(( vecx[0] == 1.0 ))) {throw std::runtime_error("assertion failed: ( vecx[0] == 1.0 )"); }
}
auto test_heap() {

	
	std::cout << std::string("heap test...") << std::endl;
	auto m1 = std::shared_ptr<std::map<std::string,std::vector<int>*>>(new std::map<std::string,std::vector<int>*>{{std::string("K1"),new std::vector<int>{0,1}}
,{std::string("K2"),new std::vector<int>{2,3}}});
	if (!(( (*(*m1)[std::string("K1")])[0] == 0 ))) {throw std::runtime_error("assertion failed: ( (*(*m1)[std::string(\"K1\")])[0] == 0 )"); }
	if (!(( (*(*m1)[std::string("K1")])[1] == 1 ))) {throw std::runtime_error("assertion failed: ( (*(*m1)[std::string(\"K1\")])[1] == 1 )"); }
	if (!(( (*(*m1)[std::string("K2")])[0] == 2 ))) {throw std::runtime_error("assertion failed: ( (*(*m1)[std::string(\"K2\")])[0] == 2 )"); }
	if (!(( (*(*m1)[std::string("K2")])[1] == 3 ))) {throw std::runtime_error("assertion failed: ( (*(*m1)[std::string(\"K2\")])[1] == 3 )"); }
	auto vec = std::get<0>(*(*tuplemap)[std::string("A")]);			/* new variable*/
	if (!(( (*vec)[0] == 1.0 ))) {throw std::runtime_error("assertion failed: ( (*vec)[0] == 1.0 )"); }
	auto vecx = std::get<0>(*(*tuplemap)[std::string("A")]);			/* tuple   */
	if (!(( (*vecx)[0] == 1.0 ))) {throw std::runtime_error("assertion failed: ( (*vecx)[0] == 1.0 )"); }
	std::cout << std::string("testing loop over map keys") << std::endl;
	for (auto &_pair_key: (*m1)) {
  auto key = _pair_key.first;
		std::cout << std::string("key:");
std::cout << key;std::cout << std::endl;
	}
	std::cout << std::string("testing loop over map keys and values") << std::endl;
	for (auto &_pair_key : *m1) {  auto key = _pair_key.first;  auto val = _pair_key.second;
		std::cout << std::string("key:");
std::cout << key;std::cout << std::endl;
		std::cout << std::string("value:");
std::cout << val;std::cout << std::endl;
	}
	auto keys = [&m1](){auto __ = std::make_shared<std::vector<decltype(m1)::element_type::key_type>>(std::vector<decltype(m1)::element_type::key_type>());for (const auto &_ : *m1) {__->push_back(_.first);}return __;}();			/* dict   */
	if (!(( keys->size() == 2 ))) {throw std::runtime_error("assertion failed: ( keys->size() == 2 )"); }
	for (auto &key: *keys) { /*loop over unknown type*/
		std::cout << key << std::endl;
	}
	if (!(( (std::find(keys->begin(), keys->end(), std::string("K1")) != keys->end()) ))) {throw std::runtime_error("assertion failed: ( (std::find(keys->begin(), keys->end(), std::string(\"K1\")) != keys->end()) )"); }
	if (!(! (( (std::find(keys->begin(), keys->end(), std::string("invalid-key")) != keys->end()) )))) {throw std::runtime_error("assertion failed: ! (( (std::find(keys->begin(), keys->end(), std::string(\"invalid-key\")) != keys->end()) ))"); }
	auto values = [&m1](){auto __ = std::make_shared<std::vector<decltype(m1)::element_type::mapped_type>>(std::vector<decltype(m1)::element_type::mapped_type>());for (auto &_ : *m1) {__->push_back(_.second);}return __;}();			/* dict   */
	if (!(( values->size() == 2 ))) {throw std::runtime_error("assertion failed: ( values->size() == 2 )"); }
}
int main() {

	
	std::cout << mymap << std::endl;
	if (!(( (*(*mymap)[std::string("key1")])[0] == 1 ))) {throw std::runtime_error("assertion failed: ( (*(*mymap)[std::string(\"key1\")])[0] == 1 )"); }
	if (!(( (*(*mymap)[std::string("key2")])[1] == 5 ))) {throw std::runtime_error("assertion failed: ( (*(*mymap)[std::string(\"key2\")])[1] == 5 )"); }
	test_heap();
	test_stack();
	std::cout << std::string("OK") << std::endl;
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
		[a1,a2,a3, A(4)],
		[a1,None],
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

class A: public std::enable_shared_from_this<A> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	int  id;
	A* __init__(int id);
	auto method();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	A() {__class__ = std::string("A"); __initialized__ = true; __classid__=0;}
	A(bool init) {__class__ = std::string("A"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
	auto A::method() {

		
		std::cout << this->id << std::endl;
	}
	A* A::__init__(int id) {

		
		this->id = id;
		return this;
	}
int main() {

	
	auto a1 = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(1); return _;}();			/* new variable*/
	auto a2 = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(2); return _;}();			/* new variable*/
	auto a3 = [&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(3); return _;}();			/* new variable*/
	/* arr = vector of vectors to: std::shared_ptr<A> */	
	auto arr = std::make_shared<std::vector<std::shared_ptr<std::vector<std::shared_ptr<A>>>>>(std::vector<std::shared_ptr<std::vector<std::shared_ptr<A>>>>{		std::shared_ptr<std::vector<decltype(a1)>>(new std::vector<decltype(a1)>{a1,a2,a3,[&](){auto _ = std::shared_ptr<A>(new A()); _->__init__(4); return _;}()}),
		std::shared_ptr<std::vector<decltype(a1)>>(new std::vector<decltype(a1)>{a1,nullptr}),
		nullptr});
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

class Parent: public std::enable_shared_from_this<Parent> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	std::shared_ptr<std::vector<std::shared_ptr<Child>>>  children;
	Parent* __init__(std::shared_ptr<std::vector<std::shared_ptr<Child>>> children);
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Parent() {__class__ = std::string("Parent"); __initialized__ = true; __classid__=0;}
	Parent(bool init) {__class__ = std::string("Parent"); __initialized__ = init; __classid__=0;}
	std::string getclassname() {return this->__class__;}
};
class Child: public std::enable_shared_from_this<Child> {
  public:
	std::string __class__;
	bool __initialized__;
	int  __classid__;
	std::weak_ptr<Parent>  parent;
	Child* __init__(std::shared_ptr<Parent> parent);
	int foo();
	auto bar();
	bool operator != (std::nullptr_t rhs) {return __initialized__;}
	bool operator == (std::nullptr_t rhs) {return !__initialized__;}
	Child() {__class__ = std::string("Child"); __initialized__ = true; __classid__=1;}
	Child(bool init) {__class__ = std::string("Child"); __initialized__ = init; __classid__=1;}
	std::string getclassname() {return this->__class__;}
};
std::shared_ptr<Child> make_child(std::shared_ptr<Parent> p) {

	
	auto c = [&](){auto _ = std::shared_ptr<Child>(new Child()); _->__init__(p); return _;}();			/* new variable*/
	p->children->push_back(c);
	return c;
}
	auto Child::bar() {

		
		std::cout << this->parent.lock()->children << std::endl;
	}
	int Child::foo() {

		
		auto par = this->parent.lock();  /* auto-fallback <_ast.Attribute object at 0x7f87bd101110> */
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
			children : std::shared_ptr<std::vector<std::shared_ptr<Child>>>
*/
	}
int main() {

	
	std::shared_ptr<std::vector<std::shared_ptr<Child>>> children( ( new std::vector<std::shared_ptr<Child>>({}) ) ); /* 1D Array */
	auto p = [&](){auto _ = std::shared_ptr<Parent>(new Parent()); _->__init__(children); return _;}();			/* new variable*/
	auto c1 = make_child(p);			/* new variable*/
	auto c2 = make_child(p);			/* new variable*/
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
	auto arr = std::make_shared<std::vector<std::shared_ptr<std::vector<int>>>>(std::vector<std::shared_ptr<std::vector<int>>>{		_sub0_arr,
		_sub1_arr});
	return arr;
	/* arrays:
		arr : int
*/
}
auto test_array(std::shared_ptr<std::vector<std::shared_ptr<std::vector<int>>>> arr) {

	
	std::cout << (*(*arr)[0])[0] << std::endl;
	/* arrays:
		arr : std::shared_ptr<std::vector<std::shared_ptr<std::vector<int>>>>
*/
}
int main() {

	
	auto a = make_array();			/* new variable*/
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

auto myfunc() {

	
	auto a = false;  /* auto-fallback <_ast.Name object at 0x7fc25eb2a590> */
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
	auto c = false;  /* auto-fallback <_ast.Name object at 0x7fc25eb2aa50> */
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
	auto b = false;  /* auto-fallback <_ast.Name object at 0x7fc25eac0090> */
	bool __finally_done_1 = false;
	try {
		std::cout << std::string("trying something that will fail...") << std::endl;
		std::cout << std::string("some call that fails at runtime") << std::endl;
		auto f = __open__(std::string("/tmp/nosuchfile"), std::string("rb"));			/* new variable*/
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
		print('a ok')
	else:
		print('not a ok')
	b = 'y'
	if b == 'x':
		print('b ok')
	else:
		print('b not ok')
```
output:
------
```c++

int main() {

	
	auto a = std::string("x");  /* auto-fallback <_ast.Str object at 0x7ffa99baf390> */
	if (( a == std::string("x") )) {
		std::cout << std::string("a ok") << std::endl;
	} else {
		std::cout << std::string("not a ok") << std::endl;
	}
	auto b = std::string("y");  /* auto-fallback <_ast.Str object at 0x7ffa99baf650> */
	if (( b == std::string("x") )) {
		std::cout << std::string("b ok") << std::endl;
	} else {
		std::cout << std::string("b not ok") << std::endl;
	}
	return 0;
}
```