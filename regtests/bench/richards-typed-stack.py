'''
Richards
'''

# based on a Java version:
#  Based on original version written in BCPL by Dr Martin Richards
#  in 1981 at Cambridge University Computer Laboratory, England
#  and a C++ version derived from a Smalltalk version written by
#  L Peter Deutsch.
#  Java version:  Copyright (C) 1995 Sun Microsystems, Inc.
#  Translation from C++, Mario Wolczko
#  Outer loop added by Alex Jacoby

from time import clock

# Task IDs
I_IDLE = 1
I_WORK = 2
I_HANDLERA = 3
I_HANDLERB = 4
I_DEVA = 5
I_DEVB = 6

# Packet types
K_DEV = 1000
K_WORK = 1001

# Packet

macro( BUFSIZE=4 )
with stack:
	BUFSIZE_RANGE = range(BUFSIZE)

	class Packet(object):

		def __init__(self,link:Packet, ident:int, kind:int):
			self.link = addr(link)
			self.ident = ident
			self.kind = kind
			let self.datum:int = 0
			let self.data : [BUFSIZE]int

		def append_to(self, lst:Packet) ->Packet:
			self.link = None
			if lst is None:
				return self
			else:
				p = lst
				next = p.link
				while next is not None:
					p = next
					next = p.link

				p.link = self
				return lst

	# Task Records

	class TaskRec(object):
		pass

	class DeviceTaskRec(TaskRec):
		def __init__(self):
			let self.pending : Packet = None

	class IdleTaskRec(TaskRec):
		def __init__(self):
			let self.control : int = 1
			let self.count   : int = 10000

	class HandlerTaskRec(TaskRec):
		def __init__(self):
			let self.work_in   : Packet = None
			let self.device_in : Packet = None

		def workInAdd(self, p:Packet) ->Packet:
			## error: taking addr of temp##self.work_in = addr(p.append_to(self.work_in))
			a = p.append_to(self.work_in)
			self.work_in = addr(a)
			return self.work_in

		def deviceInAdd(self, p:Packet) ->Packet:
			a = p.append_to(self.device_in)
			self.device_in = addr(a)
			return self.device_in

	class WorkerTaskRec(TaskRec):
		def __init__(self):
			let self.destination : int = I_HANDLERA
			let self.count       : int = 0

	# Task

	class TaskState(object):
		def __init__(self):
			let self.packet_pending:bool = True
			let self.task_waiting:bool   = False
			let self.task_holding:bool   = False

		def packetPending(self) -> self:
			self.packet_pending = True
			self.task_waiting = False
			self.task_holding = False
			return self

		def waiting(self) -> self:
			self.packet_pending = False
			self.task_waiting = True
			self.task_holding = False
			return self

		def running(self) -> self:
			self.packet_pending = False
			self.task_waiting = False
			self.task_holding = False
			return self
			
		def waitingWithPacket(self) -> self:
			self.packet_pending = True
			self.task_waiting = True
			self.task_holding = False
			return self
			
		def isPacketPending(self) -> bool:
			return self.packet_pending

		def isTaskWaiting(self) -> bool:
			return self.task_waiting

		def isTaskHolding(self) -> bool:
			return self.task_holding

		def isTaskHoldingOrWaiting(self) -> bool:
			return self.task_holding or (not self.packet_pending and self.task_waiting)

		def isWaitingWithPacket(self) -> bool:
			return self.packet_pending and self.task_waiting and not self.task_holding





	tracing = False
	layout = 0

	def trace(a:string):
		global layout
		layout -= 1
		if layout <= 0:
			print()
			layout = 50
		print(a)




	class Task(TaskState):

		# note: r:TaskRec is the super class, TODO cast to its subclass.
		def __init__(self,ident:int, priority:int, input:Packet, initialState:TaskState, handle:TaskRec):
			let self.link     : Task = taskWorkArea.taskList
			self.ident = ident
			self.priority = priority
			self.input = addr(input)

			let self.packet_pending : bool = initialState.isPacketPending()
			let self.task_waiting   : bool = initialState.isTaskWaiting()
			let self.task_holding   : bool = initialState.isTaskHolding()

			self.handle = addr(handle)  ## generic - some subclass

			taskWorkArea.taskList = self as Task
			taskWorkArea.taskTab[ident] = self as Task


		def addPacket(self,p:Packet, old:Task) -> Task:
			if self.input is None:
				self.input = addr(p)
				self.packet_pending = True
				if self.priority > old.priority:
					return self as Task
			else:
				p.append_to(self.input)
			return old

		@abstractmethod
		def fn(self, pkt:Packet, r:TaskRec) -> self:
			return self

		def runTask(self) -> Task:
			let msg : Packet = None
			if self.isWaitingWithPacket():
				msg = self.input
				self.input = msg.link
				if self.input is None:
					self.running()
				else:
					self.packetPending()

			return self.fn(msg,self.handle)


		def waitTask(self) -> self:
			self.task_waiting = True
			return self


		def hold(self) -> Task:
			taskWorkArea.holdCount += 1
			self.task_holding = True
			return self.link


		def release(self,i:int) -> Task:
			t = self.findtcb(i)
			t.task_holding = False
			if t.priority > self.priority:
				return t
			else:
				return self as Task


		def qpkt(self, pkt:Packet) -> Task:
			t = self.findtcb(pkt.ident)
			taskWorkArea.qpktCount += 1
			pkt.link = None
			pkt.ident = self.ident
			#return t.addPacket(pkt,self)
			return t.addPacket(
				pkt,
				self as Task
			)


		def findtcb(self,id:int) -> Task:
			t = taskWorkArea.taskTab[id]
			if t is None:
				print('Exception in findtcb')
			return t
				


	# DeviceTask


	class DeviceTask(Task):
		def __init__(self,i:int, p:int, w:Packet, s:TaskState, r:TaskRec):
			Task.__init__(self,i,p,w,s,r)

		#######def fn(self,pkt:*Packet, d:TaskRec) -> self:
		def fn(self,pkt:Packet, d:DeviceTaskRec) -> Task:
			if pkt is None:
				pkt = d.pending
				if pkt is None:
					return self.waitTask()
				else:
					d.pending = None
					return self.qpkt(pkt)
			else:
				d.pending = addr(pkt)
				return self.hold()



	class HandlerTask(Task):
		def __init__(self,i:int, p:int, w:Packet, s:TaskState, r:TaskRec):
			Task.__init__(self,i,p,w,s,r)

		def fn(self, pkt:Packet, h:HandlerTaskRec) -> Task:
			if pkt is not None:
				if pkt.kind == K_WORK:
					h.workInAdd(pkt)
				else:
					h.deviceInAdd(pkt)
			work = h.work_in
			if work is None:
				return self.waitTask()
			count = work.datum
			if count >= BUFSIZE:
				h.work_in = work.link
				return self.qpkt(work)

			dev = h.device_in
			if dev is None:
				return self.waitTask()

			h.device_in = dev.link
			dev.datum = work.data[count]
			work.datum = count + 1
			return self.qpkt(dev)

	# IdleTask


	class IdleTask(Task):
		def __init__(self,i:int, p:int, w:Packet, s:TaskState, r:TaskRec):
			Task.__init__(self,i,0,None,s,r)

		def fn(self,pkt:Packet, ir:TaskRec) -> Task:
			i = ir as IdleTaskRec
			i.count -= 1
			if i.count == 0:
				return self.hold()
			elif i.control & 1 == 0:
				i.control //= 2
				return self.release(I_DEVA)
			else:
				i.control = i.control//2 ^ 0xd008
				return self.release(I_DEVB)
				

	# WorkTask


	A = ord('A')

	class WorkTask(Task):
		def __init__(self,i:int, p:int, w:Packet, s:TaskState, r:TaskRec):
			Task.__init__(self,i,p,w,s,r)

		def fn(self,pkt:Packet, worker:TaskRec) -> Task:
			w = worker as WorkerTaskRec
			if pkt is None:
				return self.waitTask()

			dest = 0
			if w.destination == I_HANDLERA:
				dest = I_HANDLERB
			else:
				dest = I_HANDLERA

			w.destination = dest
			pkt.ident = dest
			pkt.datum = 0

			for i in BUFSIZE_RANGE: # xrange(BUFSIZE)
				w.count += 1
				if w.count > 26:
					w.count = 1
				pkt.data[i] = A + w.count - 1

			return self.qpkt(pkt)


	class TaskWorkArea(object):
		def __init__(self, taskTab:[]Task ):
			self.taskTab = taskTab
			let self.taskList : Task = None
			let self.holdCount:int = 0
			let self.qpktCount:int = 0


	#global_tasks = []Task(None for i in range(10))
	#global_tasks = []Task()
	let global_tasks: [10]Task

	taskWorkArea = TaskWorkArea(global_tasks)

	def schedule():
		print 'schedule...'
		t = taskWorkArea.taskList
		while t is not None:
			#pkt = None
			#if tracing:
			#	print("tcb =",t.ident)

			if t.isTaskHoldingOrWaiting():
				print 'holding.', t
				t = t.link
			else:
				###########if tracing: trace(chr(ord("0")+t.ident))
				print 'running.', t
				t = t.runTask()

	class Richards(object):

		def run(self, iterations:int) ->bool:
			for i in range(iterations):
				taskWorkArea.holdCount = 0
				taskWorkArea.qpktCount = 0

				#IdleTask(I_IDLE, 1, 10000, TaskState().running(), IdleTaskRec())  ##??
				#IdleTask(I_IDLE, 1, None, TaskState().running(), IdleTaskRec())
				tsi = TaskState()
				IdleTask(I_IDLE, 1, None, tsi.running(), IdleTaskRec())

				wkq = Packet(None, 0, K_WORK)
				wkq = Packet(wkq , 0, K_WORK)
				tsw = TaskState()
				WorkTask(I_WORK, 1000, wkq, tsw.waitingWithPacket(), WorkerTaskRec())

				wkq = Packet(None, I_DEVA, K_DEV)
				wkq = Packet(wkq , I_DEVA, K_DEV)
				wkq = Packet(wkq , I_DEVA, K_DEV)
				tsh = TaskState()
				HandlerTask(I_HANDLERA, 2000, wkq, tsh.waitingWithPacket(), HandlerTaskRec())

				wkq = Packet(None, I_DEVB, K_DEV)
				wkq = Packet(wkq , I_DEVB, K_DEV)
				wkq = Packet(wkq , I_DEVB, K_DEV)
				tsh2 = TaskState()
				HandlerTask(I_HANDLERB, 3000, wkq, tsh2.waitingWithPacket(), HandlerTaskRec())

				wkq = None;
				tsd1 = TaskState()
				tsd2 = TaskState()
				DeviceTask(I_DEVA, 4000, wkq, tsd1.waiting(), DeviceTaskRec());
				DeviceTask(I_DEVB, 5000, wkq, tsd2.waiting(), DeviceTaskRec());
				
				schedule()

				if taskWorkArea.holdCount == 9297 and taskWorkArea.qpktCount == 23246:
					pass
				else:
					return False

			return True

	def entry_point(iterations:int) ->double:
		r = Richards()
		startTime = clock()
		result = r.run(iterations)
		if not result:
			print('#ERROR incorrect results!')
		return clock() - startTime

def main():
	print global_tasks
	for ptr in global_tasks:
		assert ptr is None
	print 'starting benchmark...'
	iterations=10
	#print("#Richards benchmark (Python) starting. iterations="+str(iterations))
	total_s = entry_point(iterations)
	#print("#Total time for %s iterations: %s secs" %(iterations,total_s))
	s = total_s / iterations
	#print("#Average seconds per iteration:", s)
	print(s)
