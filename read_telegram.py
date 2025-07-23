import serial
import time

def read_all_telegrams_from_serial():
        
    ser = serial.Serial('COM6', baudrate=2400, parity=serial.PARITY_EVEN, timeout=1)

    # Send REQ_UD2 to address 1
    ser.write(bytes([0x10, 0x5B, 0x01, 0x5B, 0x16]))

    time.sleep(0.5)

    # Read response
    response = ser.read(256)
    print("Raw response:", response.hex())

    ser.close()

    return response.hex()
