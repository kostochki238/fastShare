from asyncio import new_event_loop
from inspect import BoundArguments, Signature
from inspect import iscoroutine, signature
from threading import Thread, Semaphore
from typing import Callable, Awaitable

Function = Callable | Awaitable


class RunError(Exception):
	pass


class Build:
	_func: Function = None
	_sig: Signature = None
	_ba: BoundArguments = None

	def __init__(self, func: Function):
		self._func = func
		self._sig = signature(func)

	def run(self, loop, unbound: bool = True):
		if self._ba is None:
			raise RunError("function is not built")
		args, kwargs = self._ba.args, self._ba.kwargs
		ret = self._func(*args, **kwargs)
		if iscoroutine(self._func):
			ret = loop.run_until_complete(ret)
		if unbound:
			self._ba = None
		return self

	def build(self, *args, **kwargs):
		self._ba = self._sig.bind(*args, **kwargs)
		return self._ba

	def __call__(self, *args, **kwargs):
		self.build(*args, **kwargs)
		return self


class Executor:
	class Workers(Semaphore):
		_threads: set[Thread] = set()
		_tasks: list[Build] = []
		_finished: list[Build] = []
		type_: int = 0
		INFINITE: int = 0
		STANDARD: int = 1

		def __init__(self, standard_count: int = 8, infinite_count: int = 2):
			super().__init__(self, 0)
			for inf in range(infinite_count):
				self._threads.add(
					Thread(target=self.worker, args=(self, Workers.INFINITE,))
				)

		def acquire(self, func: Callable | Awaitable | Build, *args, **kwargs):
			if isinstance(func, Build):
				self._tasks.append(func(*args, **kwargs))
			else:
				self._tasks.append(Build(func)(*args, **kwargs))
			return super().acquire(False)

		def release(self):
			super().release(self)
			return self._tasks.pop()

		def worker(self):
			loop = new_event_loop()
			while True:
				item = self.release()
				if item is not None:
					item.run(loop, self.type_ == Workers.STANDARD)
