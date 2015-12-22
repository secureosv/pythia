OSV Hello World
-------------
What is OSv? http://osv.io/

You do not need to install OSv, Pythia will automatically download and build the base image for you.
After installing Pythia, run this command, this will compile and run the example.
```bash
cd
git clone https://github.com/secureosv/pythia.git
cd pythia
sudo ./install.sh
pythia ./examples/hello_osv.md --osv
```


```pythia
#backend:c++
from runtime import *
from time import sleep
import osv/power.hh

class A:
	def __init__(self, txt:string ):
		self.txt = txt
	def foo(self):
		print self.txt

def main():
	a = A('hello world xxx')
	a.foo()
	sleep(1)
	#osv::halt()  ## hang and lock up vm
	print 'rebooting..'
	osv::reboot()

```