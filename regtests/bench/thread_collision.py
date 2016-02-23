'''
multi-threading (python3 version)
https://docs.python.org/3/library/threading.html
'''

from time import clock
import threading

A = 0
B = 0
C = 0

def test_globals():
	global A, B, C
	for i in range(10000):
		A += 1
		B += 2
		C = A + B


def main():
	print( 'starting threading test')
	starttime = clock()
	threads = []
	for i in range(10):
		t = threading.Thread( target=test_globals, args=() )
		t.start()
		threads.append( t )

	for t in threads:
		t.join()

	print( A)
	print( B)
	print( C)

main()