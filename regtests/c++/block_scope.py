'''
variable block scope
http://stackoverflow.com/questions/6167923/block-scope-in-python
'''

def main():
	for x in range(3):
		print x
		y = x

	## below is valid in python, but not in pythia.
	#assert x==2
	#assert y==x

	## note because `y` above is block scoped inside the for loop,
	## the type of `y` can be changed here.
	y = 'hi'
	print y

	print 'OK'