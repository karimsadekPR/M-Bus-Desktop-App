import sqlite3

conn = sqlite3.connect('meter_data.db')  # Connect to DB or create it if it doesn't exist
cursor = conn.cursor()  # Get a tool (cursor) to run commands

cursor.execute('''
CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    water_usage REAL
)
''')  # Create table if not already created

cursor.execute('INSERT INTO readings (timestamp, water_usage) VALUES (?, ?)',
               ('2025-07-13 15:00:00', 123.4))  # Insert a new row

conn.commit()  # Save changes
conn.close()   # Close the connection
