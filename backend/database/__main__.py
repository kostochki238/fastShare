from engine import Base, engine

if __name__ == '__main__':
	print("[SYSTEM] Creating database...")
	Base.metadata.create_all(engine)
	print("[SYSTEM] Database created successfully. Exiting...")