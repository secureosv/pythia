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