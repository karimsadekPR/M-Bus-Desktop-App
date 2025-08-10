from database import set_row_telegram

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

    parsed = parse_mbus_telegram(raw)
    if "error" in parsed:
        print(f"Parse error: {parsed['error']}")
        return

    #print(f"Parsed meter_id={parsed['meter_id']}")
    set_row_telegram(
        raw_hex=parsed["raw_hex"],
        meter_id=parsed["meter_id"],
        length=parsed["length"],
        ci_field=parsed["ci_field"]
    )
    print("Processed 1 telegram successfully.")

    PayloadData = readPayload(length=parsed["length"], raw_hex_str=parsed["raw_hex"])

    return PayloadData

def readPayload(length, raw_hex_str):

    raw_hex_str = raw_hex_str.replace(" ", "")  # Remove spaces
    raw_bytes = bytes.fromhex(raw_hex_str)

    payload_end = 4 + length

    payload = raw_bytes[4:payload_end]
    print("Payload bytes:", payload.hex())

    index = 0
    data_records = []

    while index < len(payload):
        dif = payload[index]
        index += 1

        # Extract data length from lower 4 bits of DIF
        data_length = dif & 0x0F

        vif = payload[index]
        index += 1

        data = list(payload[index:index+data_length])
        index += data_length

        data_records.append({
            'DIF': dif,
            'VIF': vif,
            'DATA': data
        })

    return data_records

def main():
    hex_string = "6823236808017245200725735105212010000004132300000002fd17ffff02fd61000001fd1f01f216"
    frame = bytes.fromhex(hex_string)
    print(process_telegram(frame))

if __name__ == "__main__":
    main()
