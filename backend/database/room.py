from engine import *


class Room(Base):
	room_id: Mapped[str] = mapped_column(default=lambda: str(_id()), unique=True)
	owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
	name: Mapped[str] = mapped_column(Computed("'Room ' | id"))

	owner: Mapped[User] = relationship(User, secondary=users_rooms, back_populates="rooms")


