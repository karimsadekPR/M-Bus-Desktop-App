import serial

def read_all_telegrams_from_serial(port="COM3", baudrate=2400, timeout=2, max_telegrams=300):
    """
    Reads raw telegrams from M-Bus serial port and returns a list of telegram bytes.
    """
    print("📡 Reading M-Bus telegrams...")
    telegrams = []

    try:
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            while len(telegrams) < max_telegrams:
                buffer = bytearray()
                while True:
                    byte = ser.read(1)
                    if not byte:
                        break  # timeout or no data
                    buffer += byte
                    if byte == b'\x16':  # End of telegram
                        break

                if buffer:
                    telegrams.append(bytes(buffer))
                else:
                    print("⚠️ No data or timeout.")
    except KeyboardInterrupt:
        print("\n🛑 Reading stopped by user.")
    except serial.SerialException as e:
        print(f"Serial error: {e}")

    return telegrams
