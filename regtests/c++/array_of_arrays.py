'''
array of arrays
'''

def main():
	## variable size vector of vectors,
	## None is allowed as a sub-vector because each sub-vector is wrapped by std::shared_ptr
	arr = [][]int(
		(1,2,3),
		(4,5,6,7,8),
		None,
		#(x*x for x in range(4)),  ## TODO fix listcomps
		(x for x in range(20)),
	)

	a,b,c = arr[0]
	assert a==1
	assert b==2
	assert c==3

	for vec in arr:
		print vec
		if vec is not None:
			x,y,z = vec
			print x,y,z

	assert len(arr)==4
	assert len(arr[0])==3
	assert len(arr[1])==5
	assert len(arr[3])==20
	assert arr[2] is None

	v = 1
	for i in arr[0]:
		assert i==v
		v+=1

	sub = arr[1]
	v = sub[0]
	for i in sub:
		assert i == v
		v+=1

	v = 0
	for i in arr[3]:
		assert i==v
		v+=1

	arr[3][0] = 1000
	arr[3][1] = 1001

	assert arr[3][0] == 1000
	assert arr[3][1] == 1001

	print 'OK'