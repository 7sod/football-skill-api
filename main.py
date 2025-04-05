from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil

from ai import run_model

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    with open("temp_video.mp4", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = run_model("temp_video.mp4")
    return JSONResponse(content={"evaluation": result})