Async Seastar Loops
-------------
https://github.com/scylladb/seastar/blob/master/doc/tutorial.md#loops


Auto Build Seastar
----------
the build script below for ubuntu (or linuxmint) is automatically run the first time you compile this markdown using this command:
`pythia seastar_do_with.md`

@https://github.com/scylladb/seastar.git
```bash
sudo apt-get install libaio-dev ninja-build ragel libhwloc-dev libnuma-dev libpciaccess-dev libcrypto++-dev libboost-all-dev libxen-dev libxml2-dev xfslibs-dev
sudo apt-get install software-properties-common python-software-properties
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install g++-4.9 gcc-4.9-multilib g++-4.9-multilib libgnutls28-dev
./configure.py --compiler=g++-4.9
ninja -j 1 build/release/libseastar
sudo cp -v ./build/release/libseastar.a /usr/local/lib/.

```


Main Script
-------------
Below `with stack:` is used to declare that all operations happen on the stack, and not the default heap.
To get the best performance with seastar stack mode is used.

The syntax below `return foo() and then (...):` is used to insert c++11 lambda functions and callbacks.

* @link:seastar
* @include:~/rusthon_cache/seastar
```rusthon
#backend:c++
import core/sleep.hh
import core/app-template.hh
import core/seastar.hh
import core/reactor.hh
import core/future-util.hh

with stack:
	def delay(seconds) -> future<>:
		sleep(seconds)
		return future

	def f() -> future<>:
		delay(1) and then():
			print 'sleep1'
		delay(2) and then():
			print 'sleep2'

		return delay(3) and then():
			print 'all done'

def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'enter on_run...'
		res = f()
		return future

	app.run(argc, argv, on_run)

```
