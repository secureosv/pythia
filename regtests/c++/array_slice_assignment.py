'''
array slice assignment syntax
'''

def somefunc():
	a = [1,2,3,4,5]
	assert len(a)==5
	b = [6,7,8,9,10]
	assert len(b)==5
	c = [100, 200]

	print('len a:', len(a))
	#for i in a:
	#	print i

	print 'slice assign front'
	lena = len(a)
	two = 2
	a[:two+1] = b
	print('len a:', len(a))
	assert len(a)==(lena-(two+1))+len(b)
	#assert len(a)==8
	for i in a: print i
	assert a[0]==6
	assert a[5]==4
	assert a[6]==5

	print 'slice assign back'
	b[2:] = c
	for i in b:
		print i
	assert b[0]==6
	assert b[1]==7
	assert b[2]==100
	assert b[3]==200
	print 'slice out of bounds'
	print a
	a[:100] = b
	for v in a:
		print v
	print 'len a:', len(a)

def stackfunc():
	print 'testing stack allocated arrays'
	with stack:
		x = [5]int(1,2,3,4,5)
		assert len(x)==5
		y = [5]int(6,7,8,9,10)
		assert len(y)==5

		z = y[3:]
		assert len(z)==2
		x[3:] = z

		for item in x:
			print item

		assert x[0]==1
		assert x[1]==2
		assert x[2]==3
		assert x[3]==9
		assert x[4]==10

def main():
	somefunc()
	stackfunc()

#main()