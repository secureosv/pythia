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


with stack:
	class Foo:
		def __init__(self, x:int ):
			self.x = x
		def add(self, y) ->int:
			return self.x + y

	def fast() -> future<int>:
		print 'fast...'
		f = Foo(400)
		r = f.add(20)
		print f.x
		return future(r)  ## gets translated to make_ready_future<T>(r)

def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'hello seastar future'

		def after_fast(val:int):
			print 'after fast...'
			print val

		fast().then( after_fast )

		return future

	app.run(argc, argv, on_run)

```
