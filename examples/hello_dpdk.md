DPDK Example
-------------
* http://dpdk.org/doc
* http://dpdk.org/doc/quick-start

Auto Build DPDK
----------
@http://dpdk.org/browse/dpdk/snapshot/dpdk-2.2.0.tar.gz
```bash
make config T=x86_64-native-linuxapp-gcc
sed -ri 's,(PMD_PCAP=).*,\1y,' build/.config
make
```

Main Script
-------------
* @link:dpdk
```pythia
#backend:c++
import CivetServer.h
from time import sleep


def main():
	print 'dpdk test...'
	std::exit(0)

```