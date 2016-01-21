# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Sokolov Yura
# modified by Tupteq
# modified by hartsantler 2014

from time import clock
#from runtime import *

DEFAULT_ARG = 9

def main():
	times = []
	for i in range(4):
		t0 = clock()
		res = fannkuch(DEFAULT_ARG)
		print( 'fannkuch flips:', res)
		tk = clock()
		times.append(tk - t0)
	avg = sum(times) / len(times)
	print(avg)

def fannkuch(n):
	count = list(range(1, n+1))
	perm1 = list(range(n))
	perm = list(range(n))
	max_flips = 0
	m = n-1
	r = n
	check = 0

	print('--------')
	print perm1
	print('________')

	while True:
		if check < 30:
			check += 1

		while r != 1:
			count[r-1] = r
			r -= 1

		if perm1[0] != 0 and perm1[m] != m:
			print '>perm 1:', perm1
			perm = perm1[:]
			print '>perm:', perm

			flips_count = 0
			k = perm[0]
			#while k:  ## TODO fix for dart
			while k != 0:
				print 'flip', k
				#perm[:k+1] = perm[k::-1]
				assert k < n
				assert k < len(perm)
				tmp = perm[k::-1]
				assert len(tmp) <= len(perm)
				#print 'tmp:', tmp
				#raise RuntimeError('x')

				## slice assignment in python
				## allows for the end slice index
				## to be greater than the length
				#assert k+1 < len(perm)  ## not always true!
				perm[:k+1] = tmp
				assert len(perm) < n+1

				print 'k+1:', k+1
				print 'len perm:', len(perm)
				print 'len tmp:', len(tmp)

				assert k+1 <= len(perm)


				flips_count += 1
				k = perm[0]

				print 'k=', k
				#if flips_count > 1:
				#	print 'breaking...'
				#	return 0
				#	break


			if flips_count > max_flips:
				max_flips = flips_count

		#print perm1
		#return 0

		do_return = True
		while r != n:
			item = perm1.pop(0)
			## python allows for the insertion index
			## to be greater than the length of the array.
			#assert r < len(perm1)  ## not always true!
			perm1.insert(r, item)
			count[r] -= 1
			if count[r] > 0:
				do_return = False
				break
			r += 1

		if do_return:
			return max_flips


main()