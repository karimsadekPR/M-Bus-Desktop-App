from pymbus import MBusSerial
from config import PORT, METER_ADDRESS

def read_meter():
    try:
        mbus = MBusSerial(PORT)
        response = mbus.send_request_frame(METER_ADDRESS)
        return response.to_JSON()
    except Exception as e:
        print("Error reading meter:", e)
        return None
