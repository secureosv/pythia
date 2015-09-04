import os, sys, subprocess

passed = []
ignore = ()

TODO_FIX = (
	'chan.py',
	'chan_universal_style.py',
	'ffi_hello.py',  ## libc is unstable as of Rust1.2
)

files = os.listdir('./rust')
files.sort()

for md in files:
	if md in TODO_FIX:
		print 'skip test: %s (TODO fix later)' %md
		continue
	elif not md.endswith('.py'):
		continue

	print md
	if md.startswith( ignore ):
		continue
	subprocess.check_call([
		'python',
		'../rusthon.py',
		'--rust',
		os.path.join('./rust', md)
	])
	passed.append( md )

print 'TESTS PASSED:'
for md in passed:
	print '	%s' %md
