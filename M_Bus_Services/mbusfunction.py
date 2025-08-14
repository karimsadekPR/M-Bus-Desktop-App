import serial
import time


controls = {
    "SND_UD": 0x7b,
    "REQ_UD2": 0x40,
}

def parse_raw_response(raw_hex):
    # Convert hex string to bytes
    data = bytes.fromhex(raw_hex)

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


def build_short_frame(control, address):
    checksum = control ^ address
    return bytes([0x10, control, address, checksum, 0x16])

def build_long_frame(SerialId):
    control = 0x73
    address = 0xFD

    frame_start = [0x68, 0x0b, 0x0b, 0x68]

    Cl = [0x52]

    data_payload = Cl + SerialId + [0xFF, 0xFF, 0xFF, 0xFF]

    checksum_data = [control, address] + data_payload
    checksum = sum(checksum_data) & 0xFF

    frame_end = [checksum, 0x16]

    frame = frame_start + [control, address] + data_payload + frame_end
    return bytes(frame)


def read_device_data(serialId):
    port="COM6"
    baudrate=2400
    try:
        ser = serial.Serial(
            port,
            baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1)
        # this is a request to restart and make the mbus ready for my request
        short_frame = build_short_frame(controls["REQ_UD2"], 0xFF)
        ser.write(short_frame)
        print("Sent short frame:", short_frame.hex())
        time.sleep(1)

        # this is the request for the data 
        print(type(serialId))
        long_frame = build_long_frame(SerialId=serialId)
        ser.write(long_frame)
        print("Sent long frame:", long_frame.hex())
        time.sleep(1)

        response = ser.read(256)
        print("Received:", response.hex())


        snd_ud_frame = build_short_frame(controls["SND_UD"], 0xFD)
        ser.write(snd_ud_frame)
        print("Sent SND_UD short frame:", snd_ud_frame.hex())
        time.sleep(1)

        response2 = ser.read(256)
        if response2:
            print(f"Response ({len(response2)} bytes): {response2.hex()}")
            return parse_raw_response(response2.hex())
        else:
            print("No response from device.")

        ser.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_device_data(serialId='')