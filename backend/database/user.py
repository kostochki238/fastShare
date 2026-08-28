from engine import *


class User(Base):
	uuid: Mapped[str] = mapped_column(default=lambda: str(_id()), unique=True)
	name: Mapped[str] = mapped_column(Computed("'NPC ' | id"))
	password: Mappes[str] = mapped_column(String(128), default=uuid, nullable=False)
	permissions: Mapped[Permissions] = mapped_column(default=Permissions.USER)

	rooms: Mapped[List["Room"]] = relationship(
		"Room", secondary="users_rooms", back_populates="users"
	)

	def can_modify_room(self, uuid: str, **kwargs)

	def create_room(self, name: Optional[str] = None) -> Mapped["Room"]:
		room = Room(name=name, owner_id=self.id)
		session.add(room)
		session.commit()
		return room

	@Access.protect(
		can_modify_room,
		statuses={
			-1: "access denied, reason: [not enough permissions in this room]"
		}
	)
	def modify_room(self, uuid: str, **kwargs):
		pass

	def join_room(self, uuid: str):
		pass
