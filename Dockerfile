FROM python:3.10-slim

# تثبيت مكتبات النظام المطلوبة لـ OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملفات المشروع
WORKDIR /app
COPY . /app

# تثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# تشغيل FastAPI عبر uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]