import sqlite3

def create_tables():
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    conn = sqlite3.connect("players.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO players (
        full_name, weight, height, diet, training, position,
        video_path, evaluation_result, source, report_path, stats_path
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        full_name, weight, height, diet, training, position,
        video_path, evaluation_result, source, report_path, stats_path
    ))

    conn.commit()
    conn.close()