continuations
-------------
"Using capture-by-move in continuations, on the other hand, is valid and very useful in Seastar applications. By moving an object into a continuation, we transfer ownership of this object to the continuation, and make it easy for the object to be automatically deleted when the continuation ends."

https://github.com/scylladb/seastar/blob/master/doc/tutorial.md#continuations



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

#def do_something( a:int, ob : std::unique_ptr<MyOb> ) -> int:
#error: could not convert ‘std::move<MyOb* const&>((* & ob))’ from ‘std::remove_reference<MyOb* const&>::type {aka MyOb* const}’ to ‘std::unique_ptr<MyOb>’
#    std::cout << do_something(a, std::move(ob)) << std::endl;

# using `auto` is optional, if not typed then allow c++14 compiler infer the type
#def do_something( a:int, ob : auto ) -> int:


def do_something( a:int, ob ) -> int:
	return ob.x + ob.y + a

def fast() -> future<int>:
	print 'fast...'
	return future(420)  ## gets translated to make_ready_future<T>(420)


def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'enter on_run...'
		with unique_ptr:
			ob = MyOb(1,2)

		## `o=move(ob)` is new c++14 capture syntax ##
		def after( a:int, ob=move(ob) ):
			print 'after got...', a
			print do_something( a, std::move(ob) )

		fast().then( after )

		return future

	app.run(argc, argv, on_run)

```
