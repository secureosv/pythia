Seastar Example
---------------
Pythia includes syntax for calling and chaining lambda functions.
The syntax below `and then():` chains a new lambda function to the previous one.
The functions are defined under `with stack:` are set to use stack memory mode (CPU Cache).
note: the default memory mode is c++11 smart pointers (reference counted garbage collection).

```python

with stack:
	def delay(seconds) -> future<>:
		print 'sleeping', seconds
		sleep(seconds)
		return future

	def f() -> future<>:
		delay(1) and then():
			print 'sleep1'
			and then():
				print 'sleep1.1'
				delay(1) and then():
					print 'nested 1.1:1'
					and then():
						print 'nested 1.1:2'

			and then():
				print 'sleep1.2'
				and then():
					print 'sleep1.2.1'

		delay(2) and then():
			print 'sleep2'

		return delay(3) and then():
			print 'all done'

```
