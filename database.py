import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def create_tables():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        full_name TEXT,
        weight REAL,
        height REAL,
        diet TEXT,
        training TEXT,
        position TEXT,
        video_path TEXT,
        evaluation_result TEXT,
        source TEXT,
        report_path TEXT,
        stats_path TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_player_data(
    full_name, weight, height, diet, training, position,
    video_path, evaluation_result, source, report_path, stats_path
):
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO players (
        full_name, weight, height, diet, training, position,
        video_path, evaluation_result, source, report_path, stats_path
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        full_name, weight, height, diet, training, position,
        video_path, evaluation_result, source, report_path, stats_path
    ))

    conn.commit()
    conn.close()