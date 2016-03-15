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
	def get_int(self):
		return 3
	def get_float(self):
		return 4.4
	def do_nothing(self):
		pass

def main():
	print returns_int( False )
	assert returns_int( False )==2
	assert returns_int( True )==1
	assert returns_float() == 1.1

	f = Foo()
	assert f.get_int()==3
	assert f.get_float()==4.4
	f.do_nothing()

	print('OK')

