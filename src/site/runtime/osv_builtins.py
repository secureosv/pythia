# OSv helper builtins
# by Brett Hartshorn - copyright 2015
# License: "New BSD"

import osv/power.hh

def __request_rebuild( reboots, sleep_seconds ):
	counter = 0

	try:
		print 'trying to readfile...'
		d = readfile( open('/reboot.log', 'r' ) )
		print d
		#counter = int( d )
		counter = inline('(int)(d[0])') - 48
		print counter
		print '--------'
	except:
		print 'first bootup...'

	counter += 1
	print counter
	#f = open('/reboot.log', 'w')
	#s=cstr(str(counter))
	#f.close()

	if counter < reboots:
		print 'sleeping...'
		#sleep( sleep_seconds )
		print 'rebooting...'
		osv::reboot()
	else:
		print 'vm shutdown...'
		osv::poweroff()