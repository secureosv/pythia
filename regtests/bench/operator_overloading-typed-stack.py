'''
bretts simple operator overloading benchmark
'''

from time import clock
from runtime import *

with stack:
	class Vector:
		def __init__(self, x:double, y:double, z:double):
			self.x = x
			self.y = y
			self.z = z

		def __add__(self, other:Vector) ->self:
			return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

		def __mul__(self, other:Vector) ->self:
			return Vector(self.x*other.x, self.y*other.y, self.z*other.z)


	#def benchmark(n) ->[][]Vector:
	def benchmark(n):
		a = [ Vector(i*0.09,i*0.05, i*0.01) for i in range(n)]
		b = [ Vector(i*0.08,i*0.04, i*0.02) for i in range(n)]
		c = []Vector()
		d = []Vector()

		for j in range(n):
			u = a[j]
			v = b[j]
			c.append( u+v )
			d.append( u*v )

		#return [][]Vector(c,d)
		#return c, d

POINTS = 100000

def test(arg) ->[]double:
	times = []double()
	for i in range(arg):
		t0 = clock()
		benchmark(POINTS)
		#o = benchmark(POINTS)
		tk = clock()
		times.append(tk - t0)
	return times
	

def main():
	times = test( 3 )
	avg = sumd(times) / len(times)
	print( avg )

