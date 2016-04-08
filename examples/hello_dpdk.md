DPDK Example
-------------
* http://dpdk.org/doc
* http://dpdk.org/doc/quick-start

requires libpcap, on ubuntu run: `sudo apt-get install libpcap-dev`

Auto Build DPDK
----------

@http://dpdk.org/browse/dpdk/snapshot/dpdk-2.2.0.tar.gz
```bash
make config T=x86_64-native-linuxapp-gcc
sed -ri 's,(PMD_PCAP=).*,\1y,' build/.config
make
sudo make install
sudo mkdir /usr/local/include/dpdk
sudo cp -Rv build/include /usr/local/include/dpdk
```

Main Script
-------------
* @link:dpdk
* @include:/usr/local/include/dpdk
```pythia
#backend:c++
import rte_memory.h
import rte_memzone.h
import rte_launch.h
import rte_eal.h
import rte_per_lcore.h
import rte_lcore.h
import rte_debug.h

def lcore_hello(arg:void*) ->int:
	#unsigned lcore_id;
	lcore_id = rte_lcore_id()
	print "hello from core:", lcore_id
	return 0

def main( argc:int, argv:char**) -> int:
	print 'dpdk test...'
	let lcore_id : unsigned
	ret = rte_eal_init(argc, argv)
	if ret < 0:
		rte_panic( "Cannot init EAL\n".cstr() );

	#/* call lcore_hello() on every slave lcore */
	inline("RTE_LCORE_FOREACH_SLAVE(lcore_id) { rte_eal_remote_launch(lcore_hello, NULL, lcore_id);}")

	#/* call it on master lcore too */
	lcore_hello(None)

	rte_eal_mp_wait_lcore()
	print 'OK'
	return 0

```