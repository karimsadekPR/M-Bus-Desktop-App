import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('meter_data.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meterId INTEGER,
    manufacturer TEXT,
    address TEXT,
    version INTEGER,
    date TEXT,
    time TEXT,
    meter_type TEXT,
    date_no INTEGER,
    value REAL,
    unit TEXT,
    description TEXT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS meters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meterId INTEGER UNIQUE,
    manufacturer TEXT,
    address TEXT,
    version INTEGER,
    meter_type TEXT
        );
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

def save_reading(meterId, manufacturer, address, version, date, time,
                 meter_type, date_no, value, unit, description, timestamp=None):
    conn = sqlite3.connect('meter_data.db')
    if timestamp is None:
        # Let the DB use default CURRENT_TIMESTAMP
        conn.execute('''
            INSERT INTO readings (meterId, manufacturer, address, version, date, time,
                                  meter_type, date_no, value, unit, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (meterId, manufacturer, address, version, date, time,
              meter_type, date_no, value, unit, description))
    else:
        conn.execute('''
            INSERT INTO readings (meterId, manufacturer, address, version, date, time,
                                  meter_type, date_no, value, unit, description, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (meterId, manufacturer, address, version, date, time,
              meter_type, date_no, value, unit, description, timestamp))
    conn.commit()
    conn.close()


def save_meter(meter_id, manufacturer=None, address=None, version=None, meter_type=None):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT id FROM meters WHERE meterId = ?', (meter_id,))
    existing = cur.fetchone()
    if existing is None:
        cur.execute('''
            INSERT INTO meters (meterId, manufacturer, address, version, meter_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (meter_id, manufacturer, address, version, meter_type))
        conn.commit()
    conn.close()


def get_all_readings():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM readings ORDER BY water_usage DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

    
def get_all_readings_id(meterId):
    with sqlite3.connect('meter_data.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT meterId, manufacturer, address, version, date, time, meter_type,
                   date_no, value, unit, description, timestamp
            FROM readings
            WHERE meterId = ? ORDER BY water_usage DESC
            ''', (meterId,))
        rows = cur.fetchall()
        return rows

def get_all_meters():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM meters')
    rows = cur.fetchall()
    conn.close()
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

def get_all_meter_ids():
    """Return a list of all meter IDs stored in the meters table."""
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()
    cur.execute('SELECT meterId FROM meters ORDER BY meterId ASC')
    rows = cur.fetchall()
    conn.close()
    # Flatten list of tuples into a list of IDs
    return [row[0] for row in rows]


