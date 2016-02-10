'''
stack memory mode
'''
with stack:
	let garr : [10]int

	def stack_test():
		let arr : [5]int
		for i in garr:
			print i
			assert i==0

		for i in arr:
			print i
			assert i==0


def main():
	stack_test()
