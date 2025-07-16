from datetime import datetime
from mbus_reader import read_meter
from database import init_db, save_reading
from gui import launch_gui

# Set up DB first
init_db()

# # Read from meter
# data = read_meter()

# if data:
#     # If real device is connected, use its values
#     timestamp = data["timestamp"]
#     usage = data["value"]
#     save_reading(timestamp, usage)
    
# Launch GUI
launch_gui()
