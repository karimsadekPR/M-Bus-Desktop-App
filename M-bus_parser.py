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

def process_telegrams(raw_telegrams):
    init_db()
    success_count = 0
    for i, raw in enumerate(raw_telegrams, 1):
        parsed = parse_mbus_telegram(raw)
        if "error" not in parsed:
            print(f"[{i}] Parsed meter_id={parsed['meter_id']}")
            set_row_telegram(
                raw_hex=parsed["raw_hex"],
                meter_id=parsed["meter_id"],
                length=parsed["length"],
                ci_field=parsed["ci_field"]
            )
            success_count += 1
        else:
            print(f"[{i}] Parse error: {parsed['error']}")
    print(f"Processed {success_count}/{len(raw_telegrams)} telegrams successfully.")



def main():
    raw_telegrams = read_all_telegrams_from_serial(max_telegrams=3)
    process_telegrams(raw_telegrams)

if __name__ == "__main__":
    main()