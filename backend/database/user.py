from .engine import *


class User(Base):
	name: Mapped[str] = mapped_column(Computed("'NPC ' | id"))
	password: Mapped[str] = mapped_column(String(128), Computed("uuid"), nullable=False)
	permissions: Mapped[Permissions] = mapped_column(default=Permissions.USER)

	rooms: Mapped[List["Room"]] = relationship(
		"Room", secondary="users_rooms", back_populates="users"
	)

	@Access.status({
		-1: "database error",
		0: "successfully created new room"
	})
	def create_room(self, name: Optional[str] = None):
		room = Room(name=name, owner_id=self.id)
		session.add(room)
		session.commit()
		return 0, room

	def can_modify(self, type_: str, uuid: str, **kwargs):
		room = globals()[type_].get_one(uuid=uuid)
		return (room.owner_id == self.id) if room is not None else True

	@Access.protect(
		can_modify,
		statuses={
			-2: "room doesn't exist",
			-1: "access denied, reason: [not enough permissions in this room]",
			0: "successfully modified"
		}
	)
	def modify(self, type_: str, uuid: str, **kwargs):
		obj = globals()[type_].get_one(uuid=uuid)
		if room:
			for arg, value in kwargs.items():
				if hasattr(room, arg):
					setattr(room, arg, value)
			return 0
		return -2

	@Access.status({
		-1: "room doesn't exist",
		0: "successfully joined room",
		1: "already joined to room"
	})
	def join_room(self, uuid: str):
		room = Room.get_one(uuid=uuid)
		if room:
			if room not in self.rooms:
				self.rooms.add(room)
				session.commit()
				return 1
			return 0
		return -1

	@Access.status({
		-1: "database error",
		0: "success upload"
	})
	def upload_file(self, name: str, size: int):
		file = File(name=name, size=size, owner_id=self.id)
		session.add(file)
		session.commit()
		return 0, file
