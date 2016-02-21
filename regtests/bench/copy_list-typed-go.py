'''copy list micro benchmark'''

from time import clock
from runtime import *

def copy_list( a:[]int, n:int ) -> [][]int:
	x = [][]int()
	for i in range(n):
		b = a[:]
		for j in range(10):
			b.append( j )
		x.append( b[...] )
	return x

def test():
	a = range(1000)
	times = []float64()
	for i in range(4):
		t0 = clock()
		_ = copy_list(a, 10000)
		tk = clock()
		times.append(tk - t0)
	avg = 0.0
	for t in times:
		avg += t
	avg /= float64( len(times) )
	print(avg)

def main():
	print 'starting...'
	test()

