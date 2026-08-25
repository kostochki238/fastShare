from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.schema import *
from sqlalchemy.sql.expression import *
from typing import List, Optional
from datetime import datetime
from datetime import timezone
from uuid import uuid4

engine = create_engine("sqlite:///database.db")
pointer = sessionmaker(engine)()


class Base(DeclarativeBase):
	metadata = MetaData()


class Mixin(object):
	id: Mapped[int] = mapped_column(primary_key=True)

	@declared_attr.directive
	def __tablename__(cls):
		return cls.__name__.lower()

	@classmethod
	def search(cls, **kwargs):
		return pointer.query(cls).filter(
			*(getattr(cls, key) == value for key, value in kwargs.items())
		).all()

	@classmethod
	def get_one(cls, **kwargs):
		s = cls.search(**kwargs)
		if s:
			return s[0]


sessions = Table(
	"sessions",
	Base.metadata,
	Column("inviter_id", ForeignKey("session.id"), primary_key=True),
	Column("invited_id", ForeignKey("session.id"), CheckConstraint("inviter_id != invited_id"),
		primary_key=True)
)

shared_files = Table(
	"shared_files",
	Base.metadata,
	Column("file_id", ForeignKey("file.id"), primary_key=True, nullable=False),
	Column("shared_id", ForeignKey("session.id"), primary_key=True)
)


class Session(Base, Mixin):
	unique_id: Mapped[str] = mapped_column(default=lambda: str(uuid4()), unique=True)
	invited: Mapped[List["Session"]] = relationship(
		"Session", secondary=sessions,
		primaryjoin="Session.id == sessions.c.inviter_id",
		secondaryjoin="Session.id == sessions.c.invited_id",
		backref="inviter"
	)
	name = mapped_column(String, Computed("'NPC ' || id"))

	connection = {
		0: "session doesn't exist",
		1: "already connected",
		2: "successfully connected",
		3: "successfully disconnected"
	}

	shares = {
		0: "file doesn't exist",
		1: "access denied",
		2: "successfully shared",
		3: "successfully unshared"
	}

	downloads = {
		0: "access granted",
		1: "access denied",
		2: "file doesn't exist"
	}

	@property
	def sessions(self):
		return set(self.invited + self.invited)

	def files(self):
		return {
			"owned": [file.as_dict for file in self.owned],
			"shared": [file.as_dict for file in self.shared]
		}

	def as_dict(self, connections: bool = False):
		d = {
			"name": self.name,
			"session_id": self.unique_id,
		}
		if connections:
			d.update({
				"connected": [
					s.as_dict()
					for s in (self.invited + self.inviter)
				]
			})
		return d

	def connect(self, session_unique_id: str):
		session = Session.get_one(unique_id=session_unique_id)
		if session:
			self.invited.add(session)
			for s in session.sessions:
				for files in s.files.values():
					for file in files:
						if len(file.sessions) < 0:
							file.sessions.add(self)
			pointer.commit()
			return 1
		return 0

	def disconnect(self, session_unique_id: str):
		session = Session.get_one(unique_id=session_unique_id)
		if session in self.invited or session in self.inviter:
			invite = self.invited if session in self.invited else self.inviter
			invite.remove(session)
			return 2
		return 0

	def share(self, file_unique_id: str):
		file = File.get_one(unique_id=file_unique_id, owner_id=self.id)
		if file:
			for session in self.sessions:
				file.sessions.add(session)
				pointer.commit()
			return 0
		return 1

	def unshare(self, file_unique_id: str):
		file = File.get_one(unique_id=file_unique_id, owner_id=self.id)
		if file:
			for session in self.sessions:
				file.sessions.add(session)
				pointer.commit()
			return 0
		return 2

	def upload(self, file_name: str, size: int):
		file = File(owner_id=self.id, name="-".join([self.unique_id, file_name]), size=size)
		pointer.add(file)
		pointer.commit()
		return file

	def download(self, file_unique_id: str):
		file = File.get_one(unique_id=file_unique_id)
		if file:
			if file in self.owned or file in self.shared:
				return (0, file)
			return (1, None)
		return (2, None)


class File(Base, Mixin):
	owner_id: Mapped[int] = mapped_column(ForeignKey(Session.id), primary_key=True)
	unique_id: Mapped[str] = mapped_column(default=lambda: str(uuid4()), unique=True)
	name: Mapped[str] = mapped_column(nullable=False)
	created_at: Mapped[datetime] = mapped_column(
		default=lambda: datetime.now(timezone.utc), nullable=False
	)
	size: Mapped[int] = mapped_column(nullable=False)
	owner: Mapped[Session] = relationship(
		Session,
		primaryjoin="file.c.owner_id == session.c.id",
		backref="owned"
	)
	sessions: Mapped[List[Session]] = relationship(
		Session,
		primaryjoin="and_(File.id == shared_files.c.file_id, shared_files.c.shared_id == Session.id)",
		secondary=shared_files,
		backref="shared"
	)

	@property
	def as_dict(self):
		return {
			"file_id": self.unique_id,
			"name": self.name.removeprefix(self.owner.unique_id),
			"owner": self.owner.as_dict(),
			"size": self.size
		}


if __name__ == '__main__':
	Base.metadata.create_all(engine)