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
import core/app-template.hh
import core/seastar.hh
import core/reactor.hh
import core/future-util.hh

with stack:
	def handle_connection(s:connected_socket, a:socket_address) -> future<>:
		output = s.output()
		input = s.input()

		return do_with( s, output, input ):
			return repeat() and then( callback=lambda:output.close() ):
				return input.read() and then( capture=[output], future=[buf] ):
					if buf:
						return output.write( move(buf) ) and then():
							return next  		## becomes stop_iteration::no
					else:
						return stop   	       ## make_ready_future<stop_iteration>(stop_iteration::yes)

	def f() -> future<>:
		let lo: listen_options
		lo.reuse_address = True

		listener=listen(make_ipv4_address({1234}), lo)
		return do_with( listener ):
			return keep_doing():
				# note in c++ example future=(connected_socket s, socket_address a)
				# c++14 is able to use `auto` even in this case, so below can be pythonic and untyped
				return listener.accept() and then(capture=[], future=[s, a]):
					#// Note we ignore, not return, the future returned by
					#// handle_connection(), so we do not wait for one
					#// connection to be handled before accepting the next one.
					handle_connection( move(s), move(a) )


def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'enter on_run...'
		res = f()
		return future

	app.run(argc, argv, on_run)

```
