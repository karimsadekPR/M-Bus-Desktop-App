import serial
import time

def read_all_telegrams_from_serial():
    ser = serial.Serial('COM6', baudrate=2400, parity=serial.PARITY_EVEN, timeout=1)

    # Wake-up (SND_NKE)
    ser.write(bytes([0x10, 0x40, 0x01, 0x16]))
    time.sleep(0.5)

    # Request UD2 (REQ_UD2)
    ser.write(bytes([0x10, 0x5B, 0x01, 0x16]))
    time.sleep(0.5)

    # Read response
    response = ser.read(256)
    print("Raw response:", response.hex())

    ser.close()

    return response.hex()

def main():
    print("Start")
    hex_data = read_all_telegrams_from_serial()
    print("Done")
    return 0

if __name__ == "__main__":
    main()
