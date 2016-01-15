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
	a[:2] = b
	print('len a:', len(a))
	assert len(a)==8
	for i in a: print i
	assert a[0]==6
	assert a[5]==3

	print 'slice assign back'
	b[2:] = c
	for i in b:
		print i
	assert b[0]==6
	assert b[1]==7
	assert b[2]==100
	assert b[3]==200


def main():
	somefunc()
