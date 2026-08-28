from .engine import *

room_files = Table(
	"room_files",
	Base.metadata,
	Column("room_id", Integer, ForeignKey("room.id"), primary_key=True),
	Column("file_id", Integer, ForeignKey("file.id"), primary_key=True)
)

users_rooms = Table(
	"users_rooms",
	Base.metadata,
	Column("room_id", Integer, ForeignKey("room.id"), primary_key=True),
	Column("user_id", Integer, ForeignKey("user.id"), primary_key=True)
)
