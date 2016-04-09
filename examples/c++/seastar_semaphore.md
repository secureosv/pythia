Seastar and Semaphores
-------------
https://github.com/scylladb/seastar/blob/master/doc/tutorial.md#limiting-parallelism-and-semaphores


Auto Build Seastar
----------
the build script below for ubuntu (or linuxmint) is automatically run the first time you compile this markdown using this command:
`pythia seastar_semaphore.md`

@https://github.com/scylladb/seastar.git
```bash
sudo apt-get install libaio-dev ninja-build ragel libhwloc-dev libnuma-dev libpciaccess-dev libcrypto++-dev libboost-all-dev libxen-dev libxml2-dev xfslibs-dev
sudo apt-get install software-properties-common python-software-properties
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt-get update
sudo apt-get install g++-4.9 gcc-4.9-multilib g++-4.9-multilib libgnutls28-dev
./configure.py --compiler=g++-4.9
ninja -j 1 build/release/libseastar.a
sudo cp -v ./build/release/libseastar.a /usr/local/lib/.
```


Main Script
-------------


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
	def slow() -> future<>:
		print 'sleeping...'
		return sleep(std::chrono::seconds(1))

	def f() -> future<>:
		limit = semaphore(100)
		return do_with(limit):
			return repeat() and then( capture=[limit], future=[] ):
				return limit.wait(1) and then( capture=[limit], future=[] ):
					def on_done():
						print 'done'
						limit.signal(1)
					slow().finally( on_done )
					return next

def main(argc:int, argv:char**):
	app = new app_template()
	def on_run():
		print 'enter on_run...'
		res = f()
		return future

	app.run(argc, argv, on_run)

```
