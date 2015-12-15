Auto Build Seastar
----------
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
* @link:seastar
* @include:~/rusthon_cache/seastar
```rusthon
#backend:c++
import core/app-template.hh
import core/reactor.hh
import core/future.hh

class MyOb:
	def __init__(self, x:int, y:int):
		self.x = x
		self.y = y

def do_something( ob : unique_ptr<MyOb> ) -> int:
	return ob.x + ob.y

def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'enter on_run...'
		ob = MyOb(1,2)

		## c++14 capture syntax ##
		def after( o=move(ob) ):
			print 'after...'
			do_something( std::move(o) )

		inline('fast().then( after )')

		return future

	app.run(argc, argv, on_run)

```
