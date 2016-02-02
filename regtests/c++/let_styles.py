'''
let syntax example
'''
NUM = 100

class Foo():
	def __init__(self):
		#let self.data : [NUM]int
		pass

let Foos: []Foo

let TwentyFoos : [20]Foo

mycomp = []int()

def main():
	print 'len mycomp:', len(mycomp)
	mycomp2 = []int()
	mycomp2.append( 10 )
	print 'len mycomp2:', len(mycomp2)


	print Foos

	print len(Foos)
	assert len(Foos) == 0

	f = Foo()
	Foos.push_back(f)
	print len(Foos)
	assert len(Foos)==1

	print len(TwentyFoos)
