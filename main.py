from datetime import datetime
from mbus_reader import read_meter
from database import init_db, save_reading
from gui import launch_gui

init_db()

launch_gui()
    