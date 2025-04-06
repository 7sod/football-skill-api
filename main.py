from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ai import run_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://v0-score-tech.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        temp_video_path = f"temp_{file.filename}"
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, run_model, temp_video_path)

        os.remove(temp_video_path)
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})