'''
array with default size
'''

class A:
	pass

def somefunc():
	a = [5]int(1,2,3,4,5)
	print('len a:', len(a))
	a.pop()
	print('len a:', len(a))
	print(a[0])
	print(a[1])

	b = [10]int()
	print('len b:', len(b))
	print b[0]
	print b[1]

	c = [10]f64( 1.1, 2.2, 3.3 )
	print c[0]
	print c[1]
	print c[2]

	x = A()
	y = A()
	d = [4]A( x,y )
	print d[0]
	print d[1]

def stackfunc():
	with stack:
		a = [5]int(1,2,3,4,5)
		print('sizeof a:', sizeof(a))  ## says 20 bytes?
		#a.pop()  ## not possible for stack allocated fixed size arrays
		print('len a:', len(a))   ## translator keeps track of the array size
		print(a[0])
		print(a[1])
		print 'testing iter loop'
		for val in a:
			print val
		print 'slice fixed size array front'
		b = a[1:]
		assert b[0]
		assert len(b)==len(a)-1
		for val in b:
			print val
		assert b[0]==2
		assert b[1]==3
		assert b[2]==4
		assert b[3]==5
		print 'slice fixed size array back'
		c = a[:2]
		assert len(c)==2
		for val in c:
			print val
		assert c[0]==1
		assert c[1]==2

		for N in range(1,10):
			d = [N]int()
			for i in range(N):
				d[i]=100 + i
			print d
			print 'sizeof:', sizeof(d)
			print 'len d:', len(d)
			for v in d:
				print v

def main():
	somefunc()
	stackfunc()
	print('OK')