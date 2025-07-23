from read_telegram import read_all_telegrams_from_serial
from database import set_row_telegram, init_db

def parse_mbus_telegram(telegram_bytes):
    """Parse and return a dict or error"""
    if len(telegram_bytes) < 9:
        return {"error": "Telegram too short"}

    start_byte = telegram_bytes[0]
    length = telegram_bytes[1]
    ci_field = telegram_bytes[6]
    id_bytes = telegram_bytes[7:11]
    meter_id = int.from_bytes(id_bytes, byteorder='little')

    return {
        "start_byte": f"{start_byte:#02x}",
        "length": length,
        "ci_field": f"{ci_field:#02x}",
        "meter_id": meter_id,
        "raw_hex": telegram_bytes.hex(" ")
    }

def process_telegram(raw):
    init_db()

    parsed = parse_mbus_telegram(raw)
    if "error" in parsed:
        print(f"Parse error: {parsed['error']}")
        return

    print(f"Parsed meter_id={parsed['meter_id']}")
    set_row_telegram(
        raw_hex=parsed["raw_hex"],
        meter_id=parsed["meter_id"],
        length=parsed["length"],
        ci_field=parsed["ci_field"]
    )

    print("Processed 1 telegram successfully.")

def main():
    hex_string = "6823236808017245200725735105212010000004132300000002fd17ffff02fd61000001fd1f01f216"
    # Convert to bytes
    frame = bytes.fromhex(hex_string)
    #raw_telegram = read_all_telegrams_from_serial()
    print(frame)
    process_telegram(frame)

if __name__ == "__main__":
    main()
