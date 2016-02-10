'''
stack memory mode
'''
with stack:
	let garr : [10]int
	grange = range(3)

	class Foo:
		def __init__(self, ok:bool):
			self.ok = ok

	let Foos : [10]Foo

	def stack_test():
		let arr : [5]int
		for i in garr:
			print i
			assert i==0
		print 'global array iter ok'
		for i in arr:
			print i
			assert i==0
		print 'local array iter ok'

		j = 0
		for i in grange:
			print i
			assert i==j
			j+=1

		print 'loop over global range ok'

		for f in Foos:
			assert f is None
		print 'foos initalized to None ok'


def main():
	stack_test()
