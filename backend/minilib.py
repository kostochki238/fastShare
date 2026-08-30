from asyncio import new_event_loop
from dataclasses import dataclass
from inspect import BoundArguments, Signature
from inspect import iscoroutine, signature
from threading import Thread, Semaphore
from typing import Callable, Awaitable
from uuid import UUID, uuid

Function = Callable | Awaitable


class Build:
	class RunError(Exception):
		pass

	class BuildError(Exception):
		pass

	@dataclass
	class Result:
		func: Function
		result: Any
		uuid: UUID

	_ba: BoundArguments = None
	_uuid: UUID = None
	_finished: bool = False
	_func: Function = None
	_sig: Signature = None

	def __init__(self, func: Function):
		self._func = func
		self._sig = signature(func)

	def run(self, loop, unbound: bool = True):
		if self._ba is None:
			raise Build.RunError("function is not built")
		args, kwargs = self._ba.args, self._ba.kwargs
		self._result = self._func(*args, **kwargs)
		if iscoroutine(self._func):
			self._result = loop.run_until_complete(ret)
		if unbound:
			self._ba = None
		self._finished = True
		return self

	@property
	def result(self):
		res = self._result
		self._result = None
		self._finished = False
		return Result(func=self._func, result=res, uuid=self._uuid)

	def build(self, uuid: UUID, *args, **kwargs):
		if self._result:
			raise Build.BuildError("first get .result property")
		self._uuid = uuid
		self._ba = self._sig.bind(*args, **kwargs)
		return self._ba

	def __call__(self, *args, **kwargs):
		self.build(*args, **kwargs)
		return self


class Executor:
	class Workers(Semaphore):
		_threads: set[Thread] = set()
		_tasks: dict[UUID, Build] = {}
		_uuid: UUID = None
		_type: int = 0
		INFINITE: int = 0
		STANDARD: int = 1

		def __init__(self, count: int = 8, type_: int = Workers.INFINITE):
			super().__init__(self, 0)
			self._type = type_
			for _ in range(count):
				self._threads.add(
					Thread(target=self.worker, args=(self, ))
				)

		def acquire(self, func: Callable | Awaitable | Build, *args, **kwargs):
			if isinstance(func, Build):
				self._tasks.append(func(*args, **kwargs))
			else:
				self._tasks.append(Build(uuid, func)(*args, **kwargs))
			return super().acquire(False)

		def release(self):
			super().release(self)
			return self._tasks.pop()

		def worker(self):
			loop = new_event_loop()
			while True:
				item = self.release()
				if item is not None:
					try:
						item.run(loop, self.type_ == Workers.STANDARD)
						if self.type_ == Workers.INFINITE:
							self.acquire(item)
					except StopInfinite:
						pass
