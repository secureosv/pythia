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

	ss = Sub(10,Sub(1)) ## segfaults because Sub(1) takes a pointer to the other and then goes out of scope.
	#sa = Sub(1)
	#ss = Sub(10,sa)
	print ss
	assert ss.x==10
	assert ss.test_pass_self()==9
