Auto Recompile OSv Image
------------------
What is OSv? http://osv.io/


@https://github.com/secureosv/pythia.git
```bash
pythia ./examples/osv_raise_rebuild.md --osv
```

@reboot.log
```
0 myreboot log file
```


```pythia
#backend:c++
from runtime import *
from time import sleep

def main():
	print 'hello rebuild...'
	print 'about to fail...'
	sleep(1)
	a = True
	if a:
		raise RuntimeError(
			#git='(optional other branch)',
			#deploy_server='https://...'
			#report_server='https://...'
			reboots = 10, ## number of times to reboot before VM shutdown
			sleep = 2     ## seconds to wait after each reboot
		)
	else:
		print 'bug fixed'

```