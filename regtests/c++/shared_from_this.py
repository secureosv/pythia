'''
std::enable_shared_from_this
'''


class Foo():
	def __init__(self, x:int):
		self.x = x
		let self.other : Foo = None

	def bar(self) -> int:
		return self.x

	def test(self) ->int:
		return callbar( self.shared_from_this() )

class Sub( Foo ):
	def __init__(self, x:int, o:Foo ):
		self.x = x
		o.other = shared_from_this()

	def submethod(self) -> int:
		a = callbar( self.shared_from_this() )
		return a * 2
	def sub(self) -> int:
		return self.x -1
	def testsub(self) -> int:
		return callsub( self.shared_from_this() )

	def test_pass_self(self) -> int:
		return self.callsub( shared_from_this() )

	def callsub(self, other:Sub) -> int:
		return other.sub()

def callbar( o:Foo ) -> int:
	return o.bar()

def callsub( o:Foo ) -> int:
	s = o as Sub
	return s.sub()


def main():
	f = Foo(10)
	assert f.test()==10

	s = Sub(100, f)
	print s.test()
	assert s.test()==100
	assert s.submethod()==200
	assert s.testsub()==99
	assert s.test_pass_self()