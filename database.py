import sqlite3
import datetime

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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS meters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meterId INTEGER
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS telegrams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        raw_hex TEXT,
        meter_id INTEGER,
        length INTEGER,
        ci_field TEXT
        )
    ''')
    conn.close()


def set_row_telegram(raw_hex, meter_id, length, ci_field):
    conn = sqlite3.connect('meter_data.db')
    c = conn.cursor()
    c.execute("select * from telegrams where meter_id = ?", (meter_id,))
    existing = c.fetchone()
    if existing is None:
        c.execute("INSERT INTO telegrams (raw_hex, meter_id, length, ci_field) VALUES (?, ?, ?, ?)",
                (raw_hex,meter_id,length,ci_field))
        conn.commit()
    conn.close()

def save_reading(meterId, timestamp, value):
    conn = sqlite3.connect('meter_data.db')
    conn.execute('''
        INSERT INTO readings (meterId, timestamp, water_usage)
        VALUES (?, ?, ?)
    ''', (meterId, timestamp, value))
    conn.commit()
    conn.close()

def save_meter(meter_id):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT id FROM meters WHERE meterId = ?', (meter_id,))
    existing = cur.fetchone()
    if existing is None:
        cur.execute('''
            INSERT INTO meters (meterId)
            VALUES (?)
        ''', (meter_id,))
        conn.commit()
    conn.close()

def get_all_readings():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM readings ORDER BY water_usage DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

    
def get_Readings_ById(meterId):
    with sqlite3.connect('meter_data.db') as conn:
        cur = conn.cursor()

        if meterId == "All":
            cur.execute('''
            SELECT DATE(timestamp) as day, SUM(water_usage) as total_usage
            FROM readings
            GROUP BY DATE(timestamp)
            ORDER BY day ASC''')
        else:
            cur.execute('''
            SELECT DATE(timestamp) as day, SUM(water_usage) as total_usage
            FROM readings
            WHERE meterId = ?
            GROUP BY DATE(timestamp)
            ORDER BY day ASC''', (meterId,))

        rows = cur.fetchall()
        return rows

def get_meter_ById(meterId):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM meters WHERE meterId = ?', (meterId,))
    row = cur.fetchone()
    conn.close()
    return row

def get_filter_date(StartDate, EndDate):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('''
                SELECT * FROM readings
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY water_usage DESC
                ''', (StartDate, EndDate))
    rows = cur.fetchall()
    conn.close()
    return rows

def delete_meter(meter_id, meter_value, meter_time):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM readings WHERE meterId = ? AND timestamp = ? AND water_usage = ?', (meter_id, meter_time, meter_value))
    conn.commit()
    conn.close()


def get_last_7_days():
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)
    tomorrow = today + datetime.timedelta(days=1)  

    with sqlite3.connect('meter_data.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT DATE(timestamp) as day, SUM(water_usage) as total_usage
            FROM readings
            WHERE timestamp >= ? AND timestamp < ?
            GROUP BY DATE(timestamp)
            ORDER BY day ASC
        ''', (seven_days_ago.isoformat(), tomorrow.isoformat()))

        rows = cur.fetchall()
    return rows

def Add_new_reading():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    


