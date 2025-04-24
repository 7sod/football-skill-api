FROM python:3.11

# تثبيت مكتبات النظام المطلوبة لـ OpenCV و ffmpeg
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع إلى الحاوية
COPY . /app

# تثبيت متطلبات المشروع
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# تشغيل التطبيق باستخدام uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]