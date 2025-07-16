import sqlite3

def init_db():
    conn = sqlite3.connect('meter_data.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        water_usage REAL
    )
    ''')
    conn.close()

def save_reading(timestamp, value):
    conn = sqlite3.connect('meter_data.db')
    conn.execute("INSERT INTO readings (timestamp, water_usage) VALUES (?, ?)", (timestamp, value))
    conn.commit()
    conn.close()

def get_latest_reading():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    conn.close()
    return row
