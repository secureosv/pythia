'''
let syntax example
'''
#NUM = 100  ## requires constant

class Foo():
	def __init__(self):
		#let self.data : [NUM]int
		let self.data : [100]int

let Foos: []Foo

let TwentyFoos : [20]Foo

mycomp = []int()
twentyints = [20]int()

gFoo = Foo()


def main():
	print gFoo

	print 'len mycomp:', len(mycomp)
	assert len(mycomp)==0

	mycomp2 = []int()
	mycomp2.append( 10 )
	print 'len mycomp2:', len(mycomp2)
	assert len(mycomp2)==1

	print Foos

	print len(Foos)
	assert len(Foos) == 0

	f = Foo()
	assert len(f.data)==100
	f.data[0] = 12
	print f.data[0]

	Foos.push_back(f)
	print len(Foos)
	assert len(Foos)==1

	print len(TwentyFoos)
	TwentyFoos[0] = f
	print TwentyFoos[0]
