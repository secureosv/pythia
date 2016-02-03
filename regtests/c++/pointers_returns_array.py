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
