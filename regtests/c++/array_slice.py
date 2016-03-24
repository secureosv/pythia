'''
array slice syntax
'''

def some_vec():
	a = []int(1,2,3,4)
	return a

def test_unknown_vectypes():
	print 'testing unknown vec types'
	v1 = some_vec()
	v2 = v1[ 1: ]
	assert v2[0]==2
	assert v2[1]==3
	assert v2[2]==4
	assert len(v2)==3
	print 'OK'

def test_known_vectypes():
	for step in range(2):
		w = range(10)
		assert len(w)==10
		assert w[0]==0
		assert w[9]==9

		r = range(10,20)
		assert r[0]==10
		assert r[1]==11

		a = [1,2,3,4,5]
		print('a addr:', a)
		print('len a:', len(a))
		assert len(a)==5
		b = a[1:]
		print('b addr (should not be `a` above):', b)
		print('len b  (should be 4):', len(b))
		assert len(b)==4

		c = a[:]
		print('c addr (should not be `a` or `b` above):', c)
		print('len c:', len(c))
		assert len(a)==len(c)
		c.append(6)
		print('len c - after append:', len(c))
		assert len(c)==6
		assert len(a)==5

		d = a[:2]
		print('len d:', len(d))
		assert len(d)==2
		assert d[0]==1
		assert d[1]==2

		print('len a:', len(a))
		e = a[::1]
		print('len e should be same as a:', len(e))
		assert len(e)==len(a)
		for i in e: print i

		f = a[::2]
		print('len f:', len(f))
		assert len(f)==3
		assert f[0]==1
		assert f[1]==3
		assert f[2]==5

		g = a[::-1]
		print '- - - -'
		for v in g:
			print v

		print('len g:', len(g))
		assert len(g)==len(a)


		assert g[0]==5
		assert g[4]==1
		#for i in g: print i

		print('---slice---')
		h = a[2::-1]
		for i in h: print i
		print('len h:', len(h))
		assert len(h)==3

		assert h[0]==3
		assert h[1]==2
		assert h[2]==1
		print('h.append')
		h.append(1000)
		h.append(1000)
		print('len h after:', len(h))
		assert len(h)==5
		#assert h[-1]==1000  ## TODO fixme
		assert h[3]==1000
		assert h[4]==1000

		#assert h.back==1000
		print('---slice assignment---')

		a[:1+1] = h
		#for i in a: print i
		print('len a:', len(a))
		assert len(a)==8

	print('somefunc done')

def main():
	print('calling somefunc')
	test_known_vectypes()
	test_unknown_vectypes()
	print('OK')

#main()