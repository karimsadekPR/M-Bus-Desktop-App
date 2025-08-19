import serial
import time

from settings.settingsService import get_settings

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

def scan_mbus(port, baudrate, parity, timeout):
    results = []

    controls = {
        "REQ_UD2": 0x5B,
        "SND_UD": 0x53
    }

    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=parity,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout / 1000
    ) as ser:
        
        # Broadcast request to wake up all meters
        ser.write(build_short_frame(controls["REQ_UD2"], 0xFF))
        time.sleep(1)

        for address in range(1, 5):  # adjust range for your network
            ser.write(build_short_frame(controls["REQ_UD2"], address))
            time.sleep(0.5)
            response = ser.read(256)

            if not response:
                print(f"No response from address {address}")
                continue

            print(f"REQ_UD2 response from {address}: {response.hex()}")
            parsed = parse_raw_response(response.hex())
            
            if "error" in parsed:
                print(f"Parsing error for address {address}: {parsed['error']}")
                continue

            # Optional: Send SND_UD to get more detailed data
            ser.write(build_short_frame(controls["SND_UD"], address))
            time.sleep(0.5)
            response2 = ser.read(256)

            if response2:
                print(f"SND_UD response from {address}: {response2.hex()}")
                parsed2 = parse_raw_response(response2.hex())
                print(parsed2)
                results.append(parsed2)
            else:
                results.append(parsed)

    return results


def read_device_data(serialId):
    settings_info = get_settings()
    port = settings_info.get("comm_port", "COM6")
    baudrate = settings_info.get("baudrate", 2400)

    parity_map = {
        "Even": serial.PARITY_EVEN,
        "None": serial.PARITY_NONE
    }
    parity_value = parity_map.get(settings_info.get("parity"), serial.PARITY_NONE)

    try:
        # ✅ Check if the port actually exists
        available_ports = [p.device for p in serial.tools.list_ports.comports()]
        if port not in available_ports:
            print(f"No device connected on {port}")
            return None

        with serial.Serial(
            port,
            int(baudrate),
            bytesize=serial.EIGHTBITS,
            parity=parity_value,
            stopbits=serial.STOPBITS_ONE,
            timeout=settings_info.get("timeout", 1000) / 1000
        ) as ser:

            # 🔹 Send REQ_UD2 short frame
            short_frame = build_short_frame(controls["REQ_UD2"], 0xFF)
            ser.write(short_frame)
            print("Sent short frame:", short_frame.hex())
            time.sleep(1)

            # 🔹 Send request with SerialId
            print(f"Sending long frame for SerialId={serialId} ({type(serialId)})")
            long_frame = build_long_frame(SerialId=serialId)
            ser.write(long_frame)
            print("Sent long frame:", long_frame.hex())
            time.sleep(1)

            response = ser.read(256)
            if response:
                print("Received first response:", response.hex())
            else:
                print("No response to long frame request")

            # 🔹 Send SND_UD short frame
            snd_ud_frame = build_short_frame(controls["SND_UD"], 0xFD)
            ser.write(snd_ud_frame)
            print("Sent SND_UD short frame:", snd_ud_frame.hex())
            time.sleep(1)

            response2 = ser.read(256)
            if response2:
                print(f"Response2 ({len(response2)} bytes): {response2.hex()}")
                return parse_raw_response(response2.hex())
            else:
                print("No response from device after SND_UD")
                return None

    except serial.SerialException as e:
        print(f"Serial error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

if __name__ == "__main__":
    read_device_data(serialId='')