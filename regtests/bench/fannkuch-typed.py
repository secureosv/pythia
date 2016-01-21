# The Computer Language Benchmarks Game
# http://shootout.alioth.debian.org/
#
# contributed by Sokolov Yura
# modified by Tupteq
# modified by hartsantler 2014

from time import clock

DEFAULT_ARG = 9


def fannkuch(n:int) ->int:
	count = range(1, n+1)
	max_flips = 0
	m = n-1
	r = n
	check = 0
	perm1 = range(n)
	perm = range(n)

	#print '-------'
	#for it in perm1:
	#	print it
	#print '_______'

	while True:
		if check < 30:
			check += 1

		while r != 1:
			count[r-1] = r
			r -= 1

		if perm1[0] != 0 and perm1[m] != m:
			print '>perm 1:'
			for kk in perm1:
				print kk
			perm = perm1[:]
			print '>perm:', perm
			for kkk in perm:
				print kkk
			flips_count = 0
			k = perm[0]
			while k != 0:
				print 'flip:', k
				assert k < n
				assert k < len(perm)
				#perm[:k+1] = perm[k::-1] #TODO
				tmp = perm[k::-1]
				print 'sliced tmp'
				assert len(tmp) <= len(perm)
				tmp.shrink_to_fit()
				print '---tmp---'
				for t in tmp:
					print t

				#tmp.shrink_to_fit()
				#print '---tmp:shrink---'
				#for t in tmp:
				#	print t


				#print '---perm---'
				#for pe in perm:
				#	print pe
				k1 = k+1
				print 'k+1:', k1
				print 'len perm:', len(perm)
				print 'len tmp:', len(tmp)

				assert k+1 <= len(perm)


				perm[:k+1] = tmp  ## TODO fix bug, length grows

				#perm = perm[:k+1]  ## backwards
				for pe in perm:
					print pe

				#perm.insert(perm.begin(), tmp.begin(), tmp.end() )
				print 'assigned tmp'
				print 'new len perm:', len(perm)
				for pe in perm:
					print pe
				assert len(perm) < n+1

				flips_count += 1
				k = perm[0]
				print 'k=', k
				if flips_count > 1:
					print 'breaking...'
					break

			print 'flips', flips_count

			if flips_count > max_flips:
				max_flips = flips_count

		do_return = True
		while r != n:
			#perm1.insert(r, perm1.pop(0))  ## TODO: in c++ vec.pop_front() returns nothing
			px = perm1.pop(0)
			#px = perm1[0]
			#perm1 = perm1[1:]

			#print 'popped', px
			#perm1.insert(r, px)
			#assert r < len(perm1)
			if r < len(perm1):
				#print 'insert'
				perm1.insert(perm1.begin()+r, px)
			else:
				#print 'append'
				perm1.append(px)

			count[r] -= 1
			if count[r] > 0:
				do_return = False
				break
			r += 1

		if do_return:
			print 'do_return'
			return max_flips


def main():
	print 'fannkuch...'
	times = []float()
	for i in range(4):
		t0 = clock()
		res = fannkuch(DEFAULT_ARG)
		print 'fannkuch flips:', res
		tk = clock()
		times.append(tk - t0)
	print 'test OK'
	avg = sumf(times) / len(times)
	print(avg)
