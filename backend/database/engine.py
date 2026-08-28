from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, \
	mapped_column, relationship, sessionmaker
from sqlalchemy.schema import CheckConstraint, Column, Computed, \
	ForeignKey, MetaData, Table  
from sqlalchemy.types import Integer, String

from datetime import datetime, timezone
from enum import IntEnum
from typing import Any, Callable, List, Optional
from uuid import uuid4 as _id

utcnow = lambda: datetime.now(timezone.utc)
engine = create_engine("sqlite:///database.db")
session = sessionmaker(engine)()


class Permissions(IntEnum):
	OWNER = -1
	SYSTEM = 0
	ADMIN = 1
	MODERATOR = 2
	USER = 3
	GUEST = 4


class SearchMixin:
	id: Mapped[int] = mapped_column(primary_key=True)
	uuid: Mapped[str] = mapped_column(default=lambda: str(_id()), unique=True)

	@declared_attr.directive
	def __tablename__(cls):
		return cls.__name__.lower()

	@classmethod
	def search(cls, **query):
		return session.query(
			getattr(cls, field) == value
			for field, value in query
		).all() or None

	@classmethod
	def get_one(cls, **query):
		s = cls.search(**query)
		if s:
			return s[0]


class Base(DeclarativeBase, SearchMixin):
	metadata = MetaData()


class Access:
	@staticmethod
	def status(statuses: dict[int, Any]):
		def wrapper(func: Callable):
			def wrapped(*args, **kwargs):
				ret = func(*args, **kwargs)
				ret = ret if isinstance(ret, tuple) else (ret, None)
				msg = {
					"status": ("info" if ret[0] >= 0 else "error"),
					"message": statuses.get(ret, "success")
				}
				return (msg, *ret[1:])

			wrapped.func = func

			if not hasattr(func, "statuses"):
				wrapped.statuses = statuses
			else:
				wrapped.statuses = func.statuses.copy()
				wrapped.statuses.update(statuses)
			return wrapped
		return wrapper

	@staticmethod
	def protect(determinator: Any, *, denied: int = -1, statuses: dict[int, str] = {}):
		determinator = determinator if isinstance(determinator, Callable) \
			else lambda *ar, **kw: determinator

		def protector(func: Callable):
			def protected(*args, **kwargs):
				try:
					if determinator(*args, **kwargs):
						return func(*args, **kwargs)
					return {
						"status": "error",
						"message": func.statuses.get(denied, "access denied")
					}, None
				except Exception as e:
					return {
						"status": "error",
						"message": "database error",
						"error": e
					}, None

			func = protected.func = Access.status(statuses)(func)
			return protected
		return protector


from .file import File
from .relations import room_files, users_rooms
from .room import Room
from .user import User
