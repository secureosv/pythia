'''
multi-threading (python3 version)
https://docs.python.org/3/library/threading.html
'''

from time import clock
import threading

THREADS=2
Checked = []
Primes = []

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
			Checked.append(i)
			if is_prime(i):
				Primes.append(i)

def main():
	print( 'starting threading test')
	starttime = clock()
	threads = []
	start = 0
	for i in range(THREADS):
		t = threading.Thread( target=findprimes, args=(start, 1000,) )
		t.start()
		threads.append( t )
		start += 500

	for t in threads:
		t.join()

	print( clock()-starttime)
	print(Primes)

main()