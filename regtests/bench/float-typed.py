'''
float numbers
'''

from time import clock

POINTS = 100000

with stack:
	class Point(object):

		def __init__(self, i:float):
			let self.x:float = std::sin(i)
			let self.y:float = std::cos(i) * 3
			let self.z:float = (self.x * self.x) / 2

		def normalize(self) ->self:
			norm = std::sqrt(
				self.x * self.x + self.y * self.y + self.z * self.z
			)
			self.x /= norm
			self.y /= norm
			self.z /= norm
			return self

		def maximize(self, other:Point ) ->self:
			if self.x < other.x: self.x = other.x
			if self.y < other.y: self.y = other.y
			if self.z < other.z: self.z = other.z
			return self


	def maximize( points:[]Point ) ->Point:
		nxt = points[0]
		slice = points[1:]
		for p in slice:
			nxt = nxt.maximize(p)
		return nxt

	def benchmark( n:int ) -> Point:
		#points = []Point(
		#	Point(i as float) for i in range(n) 
		#)
		points = []Point()
		for i in range(n):
			points.append(Point(i as float))

		for p in points:
			p.normalize()

		return maximize(points)


def test( arg:int ) ->[]float:
	times = []float()
	for i in range(arg):
		t0 = clock()
		o = benchmark(POINTS)
		with stack:
			print 'x:', o.x
			print 'y:', o.y
			print 'z:', o.z
		tk = clock()
		times.append(tk - t0)
	return times
	
def main():
	times = test( 3 )
	avg = sumf(times) / len(times)
	print( avg )
