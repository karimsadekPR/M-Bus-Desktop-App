import sqlite3
import datetime

import serial

from M_Bus_Services.mbusfunction import scan_mbus
from settings.settingsService import get_settings

def init_db():
    conn = sqlite3.connect('meter_data.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    meterId TEXT,
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
            meterId TEXT UNIQUE,
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
    cur.execute('''
                SELECT meterId, manufacturer, address, version, date, time, meter_type,
                date_no, value, unit, description, timestamp
                FROM readings
                ''')
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
            WHERE meterId = ?
            ''', (meterId,))
        rows = cur.fetchall()
        return rows

def sync_mbus_to_db():
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()

    try:
        # Step 1: Get all meters from M-Bus network
        settings_info = get_settings()
        
        parity_map = {
        "Even": serial.PARITY_EVEN,
        "None": serial.PARITY_NONE
                }
        parity_value = parity_map.get(settings_info["parity"], serial.PARITY_NONE)  # default to NONE


        mbus_readings = scan_mbus(port=settings_info["comm_port"],baudrate=settings_info["baudrate"],parity=parity_value,timeout=settings_info["timeout"])  
        # Example format:
        # [
        #   {"meter_id": 1, "meter_date": "2025-08-15", "meter_time": "14:22:05", "meter_type": "Water", "meter_value": 123.45, "meter_unit": "m³", "meter_description": "Basement"},
        #   ...
        # ]

        for reading in mbus_readings:
            meter_id = reading["meter_id"]

            # Step 2: Check if meter exists
            cur.execute("SELECT COUNT(*) FROM meters WHERE meterId = ?", (meter_id,))
            meter_exists = cur.fetchone()[0] > 0

            if not meter_exists:
                print(f"New meter found: {meter_id}, adding to database.")
                cur.execute("""
                    INSERT INTO meters (meterId, meterType, meterUnit, meterDescription)
                    VALUES (?, ?, ?, ?)
                """, (
                    meter_id,
                    reading["meter_type"],
                    reading["meter_unit"],
                    reading["meter_description"]
                ))

            # Step 3: Check if reading already exists
            cur.execute("""
                SELECT COUNT(*) FROM readings
                WHERE meterId = ?
                  AND meterDate = ?
                  AND meterTime = ?
                  AND meterValue = ?
            """, (
                meter_id,
                reading["meter_date"],
                reading["meter_time"],
                reading["meter_value"]
            ))
            reading_exists = cur.fetchone()[0] > 0

            if not reading_exists:
                print(f"New reading for meter {meter_id}, adding to database.")
                cur.execute("""
                    INSERT INTO readings (meterId, meterDate, meterTime, meterType, meterValue, meterUnit, meterDescription)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    meter_id,
                    reading["meter_date"],
                    reading["meter_time"],
                    reading["meter_type"],
                    reading["meter_value"],
                    reading["meter_unit"],
                    reading["meter_description"]
                ))
            else:
                print(f"Reading for meter {meter_id} already exists, skipping.")

        conn.commit()

    except Exception as e:
        print(f"Error syncing M-Bus: {e}")

    finally:
        conn.close()


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
                ''', (StartDate, EndDate))
    rows = cur.fetchall()
    conn.close()
    return rows

import sqlite3

def delete_Reading(meter_id, meter_date, meter_time, meter_type, meter_value, meter_unit, meter_description):
    conn = sqlite3.connect('meter_data.db')
    cur = conn.cursor()

    try:
        query = """
            DELETE FROM readings
            WHERE meterId = ?
              AND date = ?
              AND time = ?
              AND meter_type = ?
              AND value = ?
              AND unit = ?
              AND description = ?
        """
        params = (
            meter_id,
            meter_date,
            meter_time,
            meter_type,
            meter_value,
            meter_unit,
            meter_description
        )

        cur.execute(query, params)
        conn.commit()

    except Exception as e:
        print(f"Error deleting reading: {e}")

    finally:
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


