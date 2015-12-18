Async Seastar Loops
-------------
https://github.com/scylladb/seastar/blob/master/doc/tutorial.md#loops


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

new syntax test
---------------

```
#backend:c++
def f():

	return do_with( s, out, input ):
		print 'do with...'

	def all_done(out):
		out.close()

	#return repeat(out, input).then( all_done ):
	return repeat(out, input):
		def on_read(buf):
			def write_done():
				print 'write done'
				return next_iteration  ## becomes stop_iteration::no

			if buf:
				out.write(move(buf)).then( write_done )
			else:
				return stop_iteration

			return input.read() and then( capture=[out], future=[buf] ):
				if buf:
					return out.write( move(buf) ) and then():
						print 'all write done.'
						#yield
						return notdone
				else:
					return stop

			#return in.read().then([&out] (auto buf) {
			#	if (buf) {
			#		return out.write(std::move(buf)).then([] {
			#			return stop_iteration::no;
			#		});
			#	} else {
			#		return make_ready_future<stop_iteration>(stop_iteration::yes);
			#	}
			#});

```

Main Script
-------------
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
			def all_done(out):
				out.close()

			#with repeat(out, in).then( all_done ):
			#repeat(out, in).then( all_done ):

			return repeat(output, input).then( all_done ):
				return input.read() and then( capture=[output], future=[buf] ):
					if buf:
						return output.write( move(buf) ) and then():
							return continuex  ## becomes stop_iteration::no
					else:
						return halt          ## make_ready_future<stop_iteration>(stop_iteration::yes)

'''
	return do_with(std::move(s), std::move(out), std::move(in),
		[] (auto& s, auto& out, auto& in) {
			return repeat([&out, &in] {
				return in.read().then([&out] (auto buf) {
					if (buf) {
						return out.write(std::move(buf)).then([] {
							return stop_iteration::no;
						});
					} else {
						return make_ready_future<stop_iteration>(stop_iteration::yes);
					}
				});
			}).then([&out] {
				return out.close();
			});
		});
}
'''

with stack:
	def f() -> future<>:
		let lo(): listen_options
		lo.reuse_address = True

		#with do(listen(make_ipv4_address({1234}), lo)):
		#	with loop( listener ):  ## becomes `return keep_doing([&listener])` in seastar

		return do_with( listener=listen(make_ipv4_address({1234}), lo) ):
			#@capture( listener )  ## TODO
			def myloop():
				# note future=(connected_socket s, socket_address a)
				return listener.accept() and then(capture=[], future=[s, a]):
					#// Note we ignore, not return, the future returned by
					#// handle_connection(), so we do not wait for one
					#// connection to be handled before accepting the next one.
					handle_connection( move(s), move(a) )

			return keep_doing( myloop )

'''
	return do_with(listen(make_ipv4_address({1234}), lo), [] (auto& listener) {
		return keep_doing([&listener] () {
			return listener.accept().then(
				[] (connected_socket s, socket_address a) {
					// Note we ignore, not return, the future returned by
					// handle_connection(), so we do not wait for one
					// connection to be handled before accepting the next one.
					handle_connection(std::move(s), std::move(a));
				});
		});
	});
}
'''

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
