from fastapi import FastAPI, Cookie, Request, Response, \
	WebSocket, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import Session, File, pointer
from typing import List

app = FastAPI(
	title="FastShare",
	description="Sharing data with FastShare"
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:80"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"]
)

async def upload_files(session: Session, file: UploadFile):
	fl = session.upload(file.filename, file.size)
	with open(fl.name, 'w') as f:
		f.write(await file.read())

@app.middleware("http")
async def session_middleware(request: Request, call_next):
	session_id = request.cookies.get("SESSION", -1)
	session = Session.get_one(unique_id=session_id)
	response = await call_next(request)
	if session is None:
		session = Session()
		pointer.add(current_session)
		pointer.commit()
		response.set_cookie(key="SESSION", value=session.unique_id)
	return response

@app.head("/api/get/id")
async def get_id(response: Response):
	response.status_code = 200
	return response

@app.get("/api/get/files")
async def get_files(request: Request):
	session_id = request.cookies.get("SESSION", -1)
	session = Session.get_one(unique_id=session_id)
	return JSONResponse(session.files())

@app.post("/api/file/share")
async def file_share(request: Request):
	pass

@app.post("/api/file/unshare")
async def file_unshare(request: Request):
	pass

@app.get("/api/file/download"):
async def file_download(request: Request):
	pass

@app.post("/api/file/upload")
async def file_upload(files: List[UploadFile], background_tasks: BackgroundTasks):
	for file in files:
		background_tasks.add_tasks(upload_file, current_session, file)

@app.delete("/api/file/delete"):
async def file_delete(request: Request):
	pass