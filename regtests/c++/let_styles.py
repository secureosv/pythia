'''
let syntax example
'''

class Foo():
	pass

let Foos: []Foo

let TwentyFoos : [20]Foo

def main():
	print Foos

	print len(Foos)
	assert len(Foos) == 0

	f = Foo()
	Foos.push_back(f)
	print len(Foos)
	assert len(Foos)==1

	print len(TwentyFoos)
