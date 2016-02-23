'''
multi-threading
'''

from time import clock

A = 0
B = 0
C = 0

def test_globals():
	global A, B, C
	for i in range(1024*1024):
		A += 1
		B += 2
		C = A + B

def test_globals_tm():
	global A, B, C
	for i in range(1024*1024):
		with atomic:
			A += 1
			B += 2
			C = A + B

def test_nosync():
	global A,B,C
	A = 0
	B = 0
	C = 0

	threads = []std::thread()
	for i in range(4):
		t = spawn( test_globals )
		threads.append( t )

	for t in threads:
		t.join()

	print A
	print B
	print C


def main():
	print 'testing transactional atomic'
	starttime = clock()

	tmthreads = []std::thread()
	for i in range(4):
		t = spawn( test_globals_tm )
		tmthreads.append( t )

	for t in tmthreads:
		t.join()

	print clock()-starttime

	print A
	print B
	print C
