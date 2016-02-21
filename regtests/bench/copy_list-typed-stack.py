'''copy list micro benchmark'''

from time import clock
from runtime import *
with stack:
	def copy_list( a:[]int, n ) -> [][]int:
		x = [][]int()
		for i in range(n):
			b = a[:]
			for j in range(10):
				b.push_back( j )
			x.push_back( b )
		return x

	def test():
		a = range(1000)
		times = []double()
		for i in range(4):
			t0 = clock()
			res = copy_list(addr(a), 10000)
			tk = clock()
			times.append(tk - t0)
		avg = sumd(times) / len(times)
		print(avg)

def main():
	test()

main()