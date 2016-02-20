'''
stack memory mode
'''
with stack:
	let garr : [10]int
	grange = range(3)
	class Bar:
		def __init__(self, value:string):
			self.value = value

	class Foo:
		def __init__(self, ok:bool):
			self.ok = ok
			let self.arr1:  [4]Bar

	class Sub(Foo):
		def __init__(self, arr2:[4]Bar):
			#self.arr2[...] = arr2   ## should work but fails
			#self.arr2[...] = addr(arr2[0])  ## should also but work fails
			## workaround, copy data
			self.arr2[:] = arr2

	let Foos : [10]Foo


	def test_foos_vec( arr:[]Foo ):
		assert len(arr)==10
		for item in arr:
			assert item is None
			## in stack mode classes `act-like None`
			assert item.ok is False

	def test_foos_fixedarr( arr:[10]Foo):
		assert len(arr)==10
		for item in arr:
			assert item.ok is False

	def stack_test():
		let bars : [4]Bar
		bars[0] = Bar('hello')
		bars[1] = Bar('world')
		sub = Sub(bars)
		print bars[0].value
		print sub.arr2[0].value


		test_foos_fixedarr(Foos)

		with stdvec as 'std::vector<Foo>(std::begin(%s), std::end(%s))':
			vec = stdvec(Foos, Foos)
			test_foos_vec(addr(vec))

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

		comp = [ Bar('hello') for i in range(10) ]
		assert len(comp)==10
		comp.append( Bar('world') )
		assert len(comp)==11



def main():
	stack_test()
