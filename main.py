from fastapi import FastAPI, UploadFile, File , Form
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
    allow_origins=["https://v0-score-tech.vercel.app/performance-analysis"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message":"API is live"}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    full_name: str = Form(...),
    weight: float = Form(...),
    height: float = Form(...),
    diet: str = Form(...),
    training: str = Form(...),
    position: str = Form(...)
):
    try:
        temp_video_path = f"temp_{file.filename}"
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, lambda: run_model(
    temp_video_path,
    full_name="غير معروف",
    weight=0,
    height=0,
    diet="غير محدد",
    training="غير محدد",
    position="غير محدد"
))


        os.remove(temp_video_path)
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
