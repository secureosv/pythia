'''
multi-threading
'''

from time import clock

A = 0
B = 0
C = 0

def test_globals():
	global A, B, C
	for i in range(10000):
		A += 1
		B += 2
		C = A + B

def test_globals_tm():
	global A, B, C
	for i in range(10000):
		with atomic:
			A += 1
			B += 2
			C = A + B

def main():
	print 'starting threading test'
	starttime = clock()
	threads = []std::thread()
	for i in range(10):
		t = spawn( test_globals )
		threads.append( t )

	for t in threads:
		t.join()

	print A
	print B
	print C

	print 'testing transactional atomic'
	global A,B,C
	A = 0
	B = 0
	C = 0

	tmthreads = []std::thread()
	for i in range(10):
		t = spawn( test_globals_tm )
		tmthreads.append( t )

	for t in tmthreads:
		t.join()

	print A
	print B
	print C
