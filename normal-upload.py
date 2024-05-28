import os
import uuid

import aiofiles
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status

CHUNK_SIZE = 1024 * 1024 * 5  # adjust the chunk size as desired
app = FastAPI()


@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), data: str = Form(...)):
    uid = str(uuid.uuid4())
    filename = request.headers.get("Filename")
    try:
        filepath = os.path.join("./", filename)
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception:
        raise HTTPException(  # noqa: B904
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="There was an error uploading the file",
        )
    finally:
        await file.close()

    return {"message": f"Successfuly uploaded {file.filename}"}
