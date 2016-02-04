'''
returns subclasses
'''
class A:
	def __init__(self, x:int, other:A):
		self.x = x
		self.other = other
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


	print('- - - - - - - ')
	if isinstance(b, B):
		assert b.foo()==4
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

	print('end of test')