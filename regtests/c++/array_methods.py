'''
array methods: append, pop, etc.
'''

def somefunc():
	a = []int(1,2,3,4,5)
	print('len a:', len(a))
	assert len(a)==5
	b = a.pop()
	print('len a after pop:', len(a))
	assert len(a)==4
	assert b==5

	#b = a[len(a)-1]
	a.pop()
	print('len a:', len(a))
	assert len(a)==3
	print(b)
	a.insert(0, 1000)
	#a.insert(a.begin(), 1000)

	print('len a:', len(a))
	print(a[0])
	assert a[0]==1000
	assert len(a)==4

	c = a.pop(0)
	assert c==1000
	assert len(a)==3
	print 'testing insert empty array'
	empty = []int(10,20)
	#a.insert(1, empty.begin(), empty.end() ) ## TODO?
	a.insert( a.begin()+1, empty.begin(), empty.end() )
	for val in a:
		print val

	#error: invalid use of void expression a->insert(a->begin()+0, a->pop_back());
	#a.insert(0, a.pop())  ## TODO fixme

def stackfunc():
	with stack:
		arr = [5]int(1,2,3,4,5)
		print('sizeof arr:', sizeof(arr))  ## says 20 bytes?
		#val = a.pop()  ## not possible for stack allocated fixed size arrays

		## pop and insert is allowed because the array remains the same size
		## this generates a for loop that moves all elements past the insertion
		## index forward by one index.
		arr.insert(0, arr.pop())


def main():
	somefunc()
	stackfunc()
	print('OK')

