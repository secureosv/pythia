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