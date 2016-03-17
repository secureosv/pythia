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


	class FooStackSub( FooStack ):
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

		subf = FooStackSub(10, 'hello')
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
		## of methods from its parent classes.
		#x = o.test_indirect() as FooStackSub
		x = o.test_indirect()
		assert x.bar == 10
		assert x.value == 'hello'


	print('OK')

