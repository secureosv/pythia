'''
multi-threading (pythia stack lock/STM free version)
'''

from time import clock
from time import sleep

THREADS=2
macro( N=1000 )
with stack:
	let Checked : [N]bool
	let Primes  : [N]bool

	def is_prime(n:int) ->bool:
		hits = 0
		for x in range(2, n):
			for y in range(2, n):
				if x*y == n:
					hits += 1
					if hits > 1:
						return False
		return True

	def findprimes(start:int, end:int):
		invec = False
		ispri = False
		found = 0
		for i in range(start, end):
			invec = Checked[i]
			if not invec:
				Checked[i] = True
				ispri = is_prime(i)
				if ispri:
					#found += 1
					Primes[i] = True

		#print 'thread found:', found

def main():
	print( 'starting shared vector test')
	starttime = clock()
	threads = []std::thread()
	start = 0
	for i in range(THREADS):
		t = spawn(findprimes(start, 1000))
		threads.append( t )
		start += 500

	for t in threads:
		t.join()

	p = []int()
	with stack:
		for i in range(N):
			if Primes[i]:
				p->push_back(i)
				#print i

	print( clock()-starttime)
	assert len(p)==181
