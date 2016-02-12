'''
C fixed size arrays decay to pointers in C++.

'''
with stack:
	class A:
		pass

	class Bar:
		def __init__(self, x:[2]int ):
			self.x = x

	class Foo( Bar ):
		def __init__(self, x:[2]:int, y:[4]A ):
			self.x = x
			self.y = y

	def test_normal_array( arr:[]int )->int:
		return len(arr)

	def test_pointer_decay( arr:[2]int )->int:
		let b : [2]int
		b = arr
		assert b[0]==arr[0]
		assert b[1]==arr[1]
		return len(arr)

	def stack_test():
		let alist : [4]A
		let i4 = [4]int
		i2 = [2]int(10,20)

		test_pointer_decay(i2) == len(i2)



def main():
	stack_test()
