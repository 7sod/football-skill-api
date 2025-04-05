import os
from dotenv import load_dotenv
import cv2
import torch
import mediapipe as mp
from ultralytics import YOLO
import google.generativeai as genai


model = YOLO('yolov8n.pt')
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

correct_videos = ["C:\\Users\\Administrator\\Videos\\correct1.mp4"]
incorrect_videos = ["C:\\Users\\Administrator\\Videos\\incorrect1.mp4"] 
unknown_videos = ["C:\\Users\\Administrator\\Videos\\unknown 1.mp4"]


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
                if int(cls) ==32:
                    ball_positions.append(((x1 + x2) / 2, (y1 + y2) / 2))

    cap.release()
    return keypoints_data, ball_positions

def run_model(player_video_path):
    correct_data, correct_ball = extract_keypoints(correct_videos[0])
    incorrect_data, incorrect_ball = extract_keypoints(incorrect_videos[0])
    player_data, player_ball = extract_keypoints(player_video_path)

    instruction_prompt = f"""You are evaluating a football skill called "Bicycle Kick".

Here is an example of a correct performance:
Keypoints: {correct_data}
Ball movement: {correct_ball}

Here is an incorrect performance:
Keypoints: {incorrect_data}
Ball movement: {incorrect_ball}

Please remember the key differences between correct and incorrect performances."""

    model_gemini = genai.GenerativeModel(model_name="gemini-2.0-flash")
    chat = model_gemini.start_chat()
    chat.send_message(instruction_prompt)


    evaluation_prompt = f"""
Now evaluate this player's performance:
Keypoints: {player_data}
Ball movement: {player_ball}

Is it more similar to the correct or incorrect example? Explain your reasoning.
"""

    response = chat.send_message(evaluation_prompt)

    return response.text
