'''
multi-threading (python3 version)
https://docs.python.org/3/library/threading.html
'''

from time import clock
from time import sleep

THREADS=2

Checked = []int()
Primes = []int()

## TODO, fix `if item in vec` syntax
#@transaction.safe
def in_vector( vec:[]int, find:int ) ->bool:
	with atomic:
		for item in vec:
			if item == find:
				return True
		return False

@transaction.safe
def is_prime(n:int) ->bool:
	with atomic:
		hits = 0
		for x in range(2, n):
			for y in range(2, n):
				if x*y == n:
					hits += 1
					if hits > 1:
						return False
		return True

def findprimes(start:int, end:int):
	#print 'thread:start', start
	#print 'thread:end', end

	invec = False
	ispri = False
	found = 0
	for i in range(start, end):
		with transaction:
			invec = in_vector(Checked, i)
		if not invec:
			with transaction:
				Checked.push_back(i)
			#with atomic:  ## wrapping `is_prime` in `with atomic` is slow and not required
			ispri = is_prime(i)
			if ispri:
				#found += 1
				with transaction:
					Primes.push_back(i)

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

	#while len(Primes) < 181:
	#	sleep(0.01)

	print( clock()-starttime)
	#print(Primes)
	#print '------------------'
	assert len(Primes)==181
	#print( len(Primes) )
	#for p in Primes:
	#	print p
