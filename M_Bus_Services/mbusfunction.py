import serial
import time

controls = {
    "SND_UD": 0x7B,
    "REQ_UD2": 0x40,
    "ACK": 0xE5,
}

def build_short_frame(data=[]):
    return bytes(data)

def build_long_frame(serialId=[]):
    # Example long frame, change as needed for your meter
    return bytes([0x68, 0x0b, 0x0b, 0x68, 0x73, 0xfd,*serialId, 0xff, 0xff, 0xff, 0xff, 0x4f, 0x16])

def parse_raw_response(raw_hex):
    # Convert hex string to bytes
    data = bytes.fromhex(raw_hex)
    # print(data)

    result = {}

    if len(data) < 6:
        result['error'] = "Frame too short"
        return result

    # Check start bytes
    if data[0] == 0x68 and data[3] == 0x68:
        length1 = data[1]
        length2 = data[2]

        if length1 != length2:
            result['error'] = "Length bytes mismatch"
            return result

        frame_length = length1
        total_frame_len = frame_length + 6  # length + start(1) + length(2) + start(1) + checksum(1) + stop(1)

        if len(data) < total_frame_len:
            result['error'] = "Incomplete frame"
            return result

        result['frame_type'] = "long variable length"

        # Extract main parts
        result['start1'] = hex(data[0])
        result['length1'] = length1
        result['length2'] = length2
        result['start2'] = hex(data[3])
        result['control'] = hex(data[4])
        result['address'] = hex(data[5])
        result['CI'] = hex(data[6])

        # Data payload bytes (after CI to before checksum)
        payload_start = 7
        payload_end = 4 + frame_length  # start at index 4 + frame length
        result['data_payload'] = data[payload_start:payload_end].hex()

        result['checksum'] = hex(data[payload_end])
        result['stop'] = hex(data[payload_end + 1])

        # Optional: verify checksum
        checksum_calc = sum(data[4:payload_end]) & 0xFF
        result['checksum_valid'] = (checksum_calc == data[payload_end])

    else:
        # Not long frame (could be short or control frame)
        result['frame_type'] = "unknown or short frame"
        result['raw'] = raw_hex

    return result


def read_device_data(port="COM6", baudrate=2400):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )

        # Send short frame
        ser.write(build_short_frame([0x10, controls["REQ_UD2"], 0xFF, 0x3F, 0x16]))
        print("Sent short frame:", build_short_frame([0x10, controls["REQ_UD2"], 0xFF, 0x3F, 0x16]).hex())
        time.sleep(1)

        # Send long frame
        ser.write(build_long_frame(serialId=[0x52, 0x45, 0x20, 0x07, 0x25]))
        print("Sent long frame:", build_long_frame().hex())
        time.sleep(1)
        response = ser.read(256)
        print(response.hex())

        ser.write(build_short_frame([0x10, controls["SND_UD"], 0xfd, 0x78, 0x16]))
        time.sleep(1)

        # Read response
        response = ser.read(256)
        if response:
            print(f"Response ({len(response)} bytes): { response.hex()}")
        else:
            print("No response from device.")

        print(parse_raw_response(response.hex())) 

        ser.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_device_data()
