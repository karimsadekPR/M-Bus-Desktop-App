import datetime
import random

def read_meter(meterId):
    # Simulated reading
    return {
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "value": round(random.uniform(100.0, 200.0),2),
        "id": meterId
    }