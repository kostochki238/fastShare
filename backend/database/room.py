from .engine import *


class Room(Base):
	owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
	name: Mapped[str] = mapped_column(Computed("'Room ' | id"))

	files: Mapped["File"] = relationship("File", secondary="room_files", back_populates="rooms")
	owner: Mapped["User"] = relationship("User", secondary="users_rooms", back_populates="rooms")


