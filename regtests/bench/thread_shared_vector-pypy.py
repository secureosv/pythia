'''
multi-threading (pypy STM version)
note: creating too many TransactionQueue's in a loop can cause freeze.
'''

from time import clock
import transaction

THREADS=2
Checked = transaction.stmset()
Primes = transaction.stmset()

def is_prime(n):
	hits = 0
	for x in range(2, n):
		for y in range(2, n):
			if x*y == n:
				hits += 1
				if hits > 1:
					return False
	return True

def findprimes(start, end):
	for i in range(start, end):
		if i not in Checked:
			Checked.add(i)
			if is_prime(i):
				Primes.add(i)

def main():
	print( 'starting threading test')
	starttime = clock()
	threads = []
	start = 0
	#for i in range(THREADS):  ## slower than TransactionQueue
	#	t = transaction.thread.start_new_thread( findprimes, args=(start, 1000,) )
	#	threads.append( t )
	#	start += 500

	tq = transaction.TransactionQueue()
	for i in range(1000):
		def func(num):
			if is_prime(num):
				Primes.add(num)
		tq.add(func, i)
		#if i == 500: tq.run()
	tq.run()

	#while len(Primes) != 181:
	#	#print len(Primes)
	#	pass
	assert len(Primes)==181

	print( clock()-starttime)
	print(Primes)

main()