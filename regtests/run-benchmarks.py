import os, sys, subprocess

#apt-get install gnuplot transfig

passed = {}

def runbench_rs(path, name, strip=False):
	url = os.path.join(path, name)
	if os.path.isfile(url.replace('.py', '-rs.py')):
		url = url.replace('.py', '-rs.py')

	if strip:
		subprocess.check_call([
			'pythia',
			'--convert2python=/tmp/input.rapyd',
			url
		])
	else:
		open('/tmp/input.rapyd','wb').write(open(url,'rb').read())

	data = open('/tmp/input.rapyd', 'rb').read()
	data = data.replace('from runtime import *', '')
	data = data.replace('from time import clock', 'JS("var clock = function(){return (new Date()).getTime()/1000;}")')
	data = 'def list(a): return a\n' + data
	data = 'import stdlib\n' + data
	open('/tmp/input.rapyd', 'wb').write(data)
	tmpjs = '/tmp/rapyd-output.js'
	subprocess.check_call(['nodejs', '/usr/local/bin/rapydscript', '/tmp/input.rapyd', '--bare', '--beautify', '--output', tmpjs])

	#rapydata = open(tmpjs,'rb').read(),
	proc = subprocess.Popen(['nodejs', tmpjs], stdout=subprocess.PIPE)
	proc.wait()
	T = proc.stdout.read().splitlines()[0]  ## extra lines could contain compiler warnings, etc.
	return str(float(T.strip()))

def runbench_py(path, name, interp='python3', cores=None):
	data = open(os.path.join(path, name), 'rb').read()
	data = data.replace('from runtime import *', '')
	data = data.replace('with oo:', '')
	lines = []
	for ln in data.splitlines():
		if ln.strip().startswith('v8->('):
			continue
		elif ln.startswith('THREADS=') and cores:
			ln = 'THREADS=%s' %cores
		lines.append(ln)
	open('/tmp/input.py', 'wb').write('\n'.join(lines))

	subprocess.check_call([
		'pythia',
		'--convert2python=/tmp/output.py',
		'/tmp/input.py'
	])

	proc = subprocess.Popen(
		[interp, '/tmp/output.py',], stdout=subprocess.PIPE
	)
	proc.wait()

	data = proc.stdout.read()
	for line in data.splitlines():
		try:
			T = float(line.strip())
		except ValueError:
			print line

	return T

def runbench(path, name, backend='javascript', pgo=False, cores=None):
	srcpath = os.path.join(path, name)
	if cores:
		data = open(os.path.join(path, name), 'rb').read()
		srcpath = '/tmp/_benchmark.py'
		lines = []
		for ln in data.splitlines():
			if ln.startswith('THREADS='):
				ln = 'THREADS=%s' %cores
			lines.append(ln)
		open(srcpath, 'wb').write('\n'.join(lines))


	cmd = [
		'pythia', 
		'--'+backend,
		'--v8-natives',
		'--release',
		srcpath
	]
	if pgo:
		cmd.append('--gcc-pgo')

	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	proc.wait()
	T = None
	data = proc.stdout.read()
	for line in data.splitlines():
		try:
			T = float(line.strip())
			print 'bench time: ' + line
			print T
		except ValueError:
			print line

	assert T is not None

	if backend=='javascript':
		js = name[:-2] + 'js'
		passed[ name ] = open('/tmp/'+js).read().split('/*end-builtins*/')[-1]

	return T

BENCHES = [
	'thread_shared_vector.py',
	#'thread_collision.py',
]
[
	'pystone.py',
	'recursive_fib.py',
	'fannkuch.py',
	'operator_overloading.py',
	'add.py',
	'float.py',
	'copy_list.py',

	#'richards.py',
	#'nbody.py',
	#'operator_overloading_functor.py',
	#'operator_overloading_nonfunctor.py',
]
TYPED = [
	'thread_shared_vector.py',
	'thread_collision.py',
	'recursive_fib.py',
	'fannkuch.py',
	'float.py',
	'pystone.py',
	'richards.py',
	'operator_overloading.py',
	'add.py',
	'copy_list.py',
]

VsPython = {
	'pypy' : [],
	'pypy-stm': [],
	'javascript':[],
	'c++' : [],
	'c++stack' : [],
	'go' : [],
}


for name in BENCHES:
	print name
	times = {}

	#try:
	#	times['rapyd'] = runbench_rs('./bench', name)
	#except:
	#	pass
	pypystm = False
	if os.path.isfile( os.path.expanduser('~/pypy-stm-2.5.1-linux64/bin/pypy-stm') ):
		pypystm = os.path.expanduser('~/pypy-stm-2.5.1-linux64/bin/pypy-stm')

	if not '--skip-python' in sys.argv:
		times['python'] = runbench_py('./bench', name)
	times['pypy'] = runbench_py('./bench', name, interp='pypy')

	if name.startswith('thread_'):
		if not '--skip-python' in sys.argv:
			times['python(single)'] = runbench_py('./bench', name, cores=1)

		times['pypy(single)'] = runbench_py('./bench', name, interp=pypystm, cores=1)

	if pypystm:
		times['pypy-stm'] = runbench_py('./bench', name, interp=pypystm)
		if name.startswith('thread_'):
			times['pypy-stm(single)'] = runbench_py('./bench', name, interp=pypystm, cores=1)

	if not name.startswith('thread_'):
		times['javascript'] = runbench('./bench', name, 'javascript')

	if name in TYPED:
		nametyped = name.replace('.py','-typed.py')
		#times['rust'] = runbench('./bench', nametyped, 'rust')

		gotyped = name.replace('.py','-typed-go.py')
		if os.path.isfile('./bench/'+gotyped):
			times['go'] = runbench('./bench', gotyped, 'go')
		elif '--go' in sys.argv:
			times['go'] = runbench('./bench', nametyped, 'go')


		times['c++']  = runbench('./bench', nametyped, 'c++')
		if os.path.isfile('rusthon-c++-build.gcda'):
			print 'removing old .gcda (PGO dump)'
			os.unlink('rusthon-c++-build.gcda')

		if name.startswith('thread_'):
			times['c++(single)']  = runbench('./bench', nametyped, 'c++', cores=1)

		nametyped = name.replace('.py','-typed-stack.py')
		if os.path.isfile('./bench/'+nametyped):
			times['c++stack']  = runbench('./bench', nametyped, 'c++')

		## only faster with if/else branches?
		#times['c++PGO']  = runbench('./bench', nametyped, 'c++', pgo=True)
		#if not os.path.isfile('rusthon-c++-build.gcda'):
		#	raise RuntimeError('failed to compile PGO optimized binary')

	print times
	perf_header = [
		'font=Helvetica',
		'fontsz=12',
		'=color_per_datum',
		'yformat=%g',
	]
	if name=='pystone.py':
		perf_header.append('ylabel=Pystones')
	else:
		perf_header.append('ylabel=seconds')

	perf = []
	if 'python' in times:
		perf.append('Python3 %s' % times['python'])
	if 'pypy' in times:
		perf.append('PyPy %s' % times['pypy'])
	if 'python(single)' in times:
		perf.append('Python3(single) %s' % times['python(single)'])
		
	if 'pypy(single)' in times:
		perf.append('PyPy(single) %s' % times['pypy(single)'])

	if 'pypy-stm' in times:
		if 'pypy-stm(single)' in times:
			perf.append('PyPy-STM(single) %s' % times['pypy-stm(single)'])
			perf.append('PyPy-STM(multi) %s' % times['pypy-stm'])
		else:
			perf.append('PyPy-STM %s' % times['pypy-stm'])

	if 'javascript' in times:
		perf.append('Pythia->JS %s' % times['javascript'])

	if 'rapyd' in times:
		perf.append('RapydScript %s' % times['rapyd'])
	if 'c++' in times:
		if 'thread' in name:
			if 'c++(single)' in times:
				perf.append('Pythia->C++STM(single) %s' % times['c++(single)'])
				perf.append('Pythia->C++STM(multi) %s' % times['c++'])
			else:
				perf.append('Pythia->C++STM %s' % times['c++'])
		else:
			perf.append('Pythia->C++ %s' % times['c++'])

	if 'c++stack' in times:
		perf.append('Pythia->C++STACK %s' % times['c++stack'])

	if 'c++PGO' in times:
		perf.append('Pythia->C++PGO %s' % times['c++PGO'])


	if 'go' in times:
		perf.append('Pythia->Go %s' % times['go'])


	perf_path = '/tmp/%s.perf' %name
	open( perf_path, 'wb' ).write( '\n'.join( perf_header+perf ).encode('utf-8') )
	os.system( './bargraph.pl -eps %s > /tmp/%s.eps' %(perf_path,name))
	subprocess.check_call([
		'convert', 
		'-density', '400', 
		'/tmp/%s.eps' % name, 
		'-resize', '1400x1600', 
		'-transparent', 'white',
		'./bench/%s.png' % name
	])

	for tag in times:
		if tag=='python':
			continue
		if name=='pystone.py':
			score = times[tag] / times['python']
		else:
			score = times['python'] / times[tag]
		print '%s: %s times faster than python' %(tag, score)
		VsPython[tag].append(score)

print VsPython

if len(BENCHES) > 4:

	Titles = {
		'python' : 'Python3 %s',
		'pypy' : 'PyPy %s',
		'pypy-stm' : 'PyPy-STM %s',
		'javascript' : 'Pythia->JS %s',
		'c++' : 'Pythia->C++ %s',
		'c++stack' : 'Pythia->C++STACK %s',
		'go' : 'Pythia->GO %s',
	}

	perf = [
		'font=Helvetica',
		'fontsz=12',
		'=color_per_datum',
		'yformat=%g',
		'ylabel=speed'
	]

	for key in VsPython:
		if VsPython[key] and key in Titles and len(VsPython[key]) >= 4:
			scores = VsPython[key]
			avg =  sum(scores) / len(scores)
			perf.append( Titles[key] % avg )

	name = 'speed-vs-python'
	perf_path = '/tmp/%s.perf' %name
	open( perf_path, 'wb' ).write( '\n'.join( perf ).encode('utf-8') )
	os.system( './bargraph.pl -eps %s > /tmp/%s.eps' %(perf_path,name))
	subprocess.check_call([
		'convert', 
		'-density', '400', 
		'/tmp/%s.eps' % name, 
		'-resize', '1400x1600', 
		'-transparent', 'white',
		'./bench/%s.png' % name
	])
