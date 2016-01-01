# OSv helper builtins
# by Brett Hartshorn - copyright 2015
# License: "New BSD"

import osv/power.hh

def __request_rebuild( reboots, sleep_seconds ):
	counter = 0

	try:
		d = readfile( open('/log.reboot.counter', 'r' ) )
		#counter = int( d )
		counter = inline('(int)(d[0])')
	except:
		print 'first bootup...'

	counter += 1
	print counter
	f = open('/log.reboot.counter', 'w')
	f.write( cstr(str(counter)), 1 )
	f.close()

	if counter < reboots:
		print 'sleeping...'
		#sleep( sleep_seconds )
		print 'rebooting...'
		osv::reboot()
	else:
		print 'vm shutdown...'
		osv::poweroff()