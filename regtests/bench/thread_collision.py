'''
multi-threading (python3 version)
https://docs.python.org/3/library/threading.html
'''

from time import clock
import threading

THREADS=2
lock = threading.Lock()

A = 0
B = 0
C = 0

def test_globals():
	global A, B, C
	for i in range(1024*1024):
		lock.acquire()
		A += 1
		B += 2
		C = A + B
		lock.release()


def main():
	print( 'starting threading test')
	starttime = clock()
	threads = []
	for i in range(THREADS):
		t = threading.Thread( target=test_globals, args=() )
		t.start()
		threads.append( t )

	for t in threads:
		t.join()

	print( clock()-starttime)
	print('A:', A)
	print('B:', B)
	print('C:', C)

main()