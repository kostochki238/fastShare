from .engine import *

class File(Base):
	owner_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
	name: Mapped[str] = mapped_column(nullable=False)
	size: Mapped[int] = mapped_column(nullable=False)
	created_at: Mapped[datetime] = mapped_column(default=utcnow(), nullable=False)

	owner: Mapped["User"] = relationship("User", back_populates="owned_files")
	rooms: Mapped[List["Room"]] = relationship(
		"Room", secondary="room_files", back_populates="files"
	)