import sqlite3

def init_db():
    conn = sqlite3.connect('meter_data.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meterId INTEGER,
        timestamp TEXT,
        water_usage REAL
    )
    ''')
    conn.close()

def save_reading(meterId,timestamp, value):
    conn = sqlite3.connect('meter_data.db')
    conn.execute("INSERT INTO readings (meterId, timestamp, water_usage) VALUES (?, ?, ?)", (meterId,timestamp, value))
    conn.commit()
    conn.close()
    
def get_all_readings():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM readings ORDER BY id DESC")  # Get all rows, newest first
    rows = cur.fetchall()  # Fetch all results
    conn.close()
    return rows  # Returns a list of tuples
