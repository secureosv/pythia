'''
std::tuple<Type1, Type2, etc...>
'''
with typedef:
	HeapTArray = []tuple( []float, []float, float )

## IDX needs to be a constant so std::get<IDX> can be resolved at compile time.
with constant: IDX = 0

with stack:
	with typedef:
		StackTArray = []tuple( []float, []float, float )

	def test_stack_array( arr: StackTArray ):
		print 'len of arr:', len(arr)

	def test_stack():
		print 'stack test'
		tuplearray = []tuple( []float, []float, float )
		a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
		b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
		tuplearray.append( a )
		tuplearray.append( b )
		test_stack_array( tuplearray )

		with get as "std::get<%s>(%s)":
			for item in tuplearray:
				vec3 = get(0, item)
				vec2 = get(1, item)
				num  = get(2, item)
				print vec3[0], vec3[1], vec3[2]

				v3 = item[{ IDX }]
				assert v3[0]==vec3[0]

				v4 = tuple.get(item, 0)
				assert v4[0]==v3[0]



def test_heap_array( arr: HeapTArray ):
	print 'len of arr:', len(arr)

def test_returns_array_of_tuples(n) -> []tuple(float, float):
	r = []tuple( float, float )
	for i in range(n):
		t = (1.1, 1.2)
		r.append(t)
	return r

## note: g++4.9 can not guess a complex return type, when the parameter `n` is untyped, 
## so `n:int` is required so the return type can automatically be deduced by g++.
def test_array_of_nested_tuples(n:int):
	with typedef: T = tuple(float,float)
	r = []tuple( T, T )

	for i in range(n):
		a = (1.1, 1.2)
		b = (2.2, 2.3)
		#r.append( (a,b) )  ## TODO
		c = (a,b)
		r.append( c )
	return r



def test_heap():
	print 'heap test'
	nested = test_array_of_nested_tuples(4)
	assert len(nested)==4

	tarr = test_returns_array_of_tuples(3)
	assert len(tarr)==3

	tuplearray = []tuple( []float, []float, float )
	a = ( [1.1,2.2,3.3], [4.4,5.5], 100.0 )
	b = ( [6.1,7.2,8.3], [9.4,0.5], 1.0 )
	tuplearray.append( a )
	tuplearray.append( b )

	test_heap_array( tuplearray )

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

		v4 = tuple.get(item, 0)
		assert v4[0]==v3[0]

def main():
	test_stack()
	test_heap()
