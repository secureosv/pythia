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

def main():
	print 'hello world'

```