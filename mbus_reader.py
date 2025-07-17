#from libmbus.mbus_serial import MBusSerial
#from config import PORT, METER_ADDRESS

#def read_meter():
 #   try:
  #      mbus = MBusSerial(PORT)
  #      response = mbus.send_request_frame(METER_ADDRESS)
  #      return response.to_JSON()
  #  except Exception as e:
  #      print("Error reading meter:", e)
  #      return None

from datetime import datetime
import random

def read_meter(meterId):
    # Simulated reading
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "value": round(random.uniform(100.0, 200.0),2),
        "id": meterId
    }