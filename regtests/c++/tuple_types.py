'''
std::tuple<Type1, Type2, etc...>
'''
#mytuple = []tuple( []double, []double, double )

with constant:
	IDX = 0

def test_stack():
	print 'stack test'
	with stack:
		tuplearray = []tuple( []float, []float, float )
		a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
		b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
		tuplearray.append( a )
		tuplearray.append( b )

		with get as "std::get<%s>(%s)":
			for item in tuplearray:
				vec3 = get(0, item)
				vec2 = get(1, item)
				num  = get(2, item)
				print vec3[0], vec3[1], vec3[2]

				v3 = item[{ IDX }]
				assert v3[0]==vec3[0]


def test_heap():
	print 'heap test'
	tuplearray = []tuple( []float, []float, float )
	a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
	b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
	tuplearray.append( a )
	tuplearray.append( b )

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

		#for s in item:
		#	print s

def main():
	test_stack()
	test_heap()
