from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os

from ai import run_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://v0-score-tech.vercel.app/"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        # حفظ الفيديو مؤقتًا
        temp_video_path = f"temp_{file.filename}"
        with open(temp_video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # تحليل الفيديو
        result = run_model(temp_video_path)

        # حذف الملف المؤقت
        os.remove(temp_video_path)

        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})