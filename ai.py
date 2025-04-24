import os
from dotenv import load_dotenv
import cv2
import torch
import mediapipe as mp
from ultralytics import YOLO
import google.generativeai as genai
import sqlite3
import glob
from database import save_player_data


# إعداد الموديلات
model = YOLO('yolov8n.pt')
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# تحميل مفتاح API
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# استخراج أسماء المهارات من المجلد
def list_all_skills():
    return [d for d in os.listdir("videos/correct") if os.path.isdir(f"videos/correct/{d}")]

# استخراج نقاط الجسم ومواقع الكرة من الفيديو
def extract_keypoints(video_path):
    cap = cv2.VideoCapture(video_path)
    keypoints_data = []
    ball_positions = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result_pose = pose.process(rgb_frame)
        if result_pose.pose_landmarks:
            keypoints = [(lm.x, lm.y) for lm in result_pose.pose_landmarks.landmark]
            keypoints_data.append(keypoints)

        results = model(frame)
        for result in results:
            for box in result.boxes.data:
                x1, y1, x2, y2, conf, cls = box.tolist()
                if int(cls) == 32:
                    ball_positions.append(((x1 + x2) / 2, (y1 + y2) / 2))

    cap.release()
    return keypoints_data, ball_positions

# حساب المتوسطات من أجل تقليل التوكنز
def average_keypoints_per_frame(data):
    return sum(len(frame) for video in data for frame in video) / max(1, sum(len(video) for video in data))

def average_ball_positions(data):
    return sum(len(ball_list) for ball_list in data) / max(1, len(data))

# الدالة الأساسية لتشغيل النموذج
def run_model(player_video_path, full_name, weight, height, diet, training, position):
    player_data, player_ball = extract_keypoints(player_video_path)

    # حساب المعدل المتوسط لاكتشاف الكرة في مقاطع الفيديو
    avg_player_ball = sum([len(ball) for ball in player_ball]) / len(player_ball) if player_ball else 0

    all_skills = list_all_skills()
    model_gemini = genai.GenerativeModel(model_name="gemini-2.0-flash")
    chat = model_gemini.start_chat()

    best_match = None
    best_reasoning = ""
    best_similarity_score = -1

    for skill in all_skills:
        correct_videos = glob.glob(f"videos/correct/{skill}/*.mp4")
        incorrect_videos = glob.glob(f"videos/incorrect/{skill}/*.mp4")

        # حساب المعدلات المتوسطة لاكتشاف الكرة في الأمثلة الصحيحة والخاطئة
        avg_correct_ball = sum([len(extract_keypoints(video)[1]) for video in correct_videos]) / len(correct_videos) if correct_videos else 0
        avg_incorrect_ball = sum([len(extract_keypoints(video)[1]) for video in incorrect_videos]) / len(incorrect_videos) if incorrect_videos else 0

        # تعديل الـ prompt ليحتوي فقط على المعدلات المتوسطة بدلاً من تفاصيل كثيرة
        instruction_prompt = f"""You are evaluating a football skill: "{skill}".
Correct examples average ball detections: {avg_correct_ball}
Incorrect examples average ball detections: {avg_incorrect_ball}
Now evaluate this player's performance with average ball detections: {avg_player_ball}
Please respond in Arabic with a score between 0 and 1, explain the reasoning in Arabic, and provide formal advice for the player on how to improve their skill."""

        # إرسال الرسالة للنموذج
        response = chat.send_message(instruction_prompt)
        text = response.text

        # استخراج السكور من النص
        try:
            score = float(text.split("score")[1].split()[0])
        except:
            score = 0.5  # في حال ما قدر يستخرج السكور

        if score > best_similarity_score:
            best_similarity_score = score
            best_match = skill
            best_reasoning = text

    # الحفظ في قاعدة البيانات بعد التقييم
    save_player_data(
    full_name=full_name,
    weight=weight,
    height=height,
    diet=diet,
    training=training,
    position=position,
    video_path=player_video_path,
    evaluation_result=best_reasoning,
    source="score tech",
    report_path=None,
    stats_path=None
)


    return {
        "skill_detected": best_match,
        "score": best_similarity_score,
        "evaluation": best_reasoning
    }