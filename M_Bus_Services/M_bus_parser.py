def parse_mbus_payload(frame=None):
    if frame is None:
        frame = {
            'frame_type': 'long variable length',
            'start1': '0x68',
            'length1': 35,
            'length2': 35,
            'start2': '0x68',
            'control': '0x8',
            'address': '0x1',
            'CI': '0x72',
            'data_payload': '45200725735105219610000004134300000002fd17ffff02fd61000001fd1f01',
            'checksum': '0x88',
            'stop': '0x16',
            'checksum_valid': True
        }
    payload_hex = frame["data_payload"]
    payload = bytes.fromhex(payload_hex)

    result = {
        "ID": None,
        "Manufacturer": None,
        "Address": frame["address"],
        "Version": None,
        "Date": None,
        "Time": None,
        "Meter Type": None,
        "Data Records": []
    }

    meter_id = payload[0:4]  
    result["ID"] = meter_id.hex()  

    manuf_code = int.from_bytes(payload[4:6], byteorder="little")

    def decode_manufacturer(code):
        c1 = chr(((code >> 10) & 0x1F) + 64)
        c2 = chr(((code >> 5) & 0x1F) + 64)
        c3 = chr((code & 0x1F) + 64)
        return f"{c1}{c2}{c3}"

    result["Manufacturer"] = decode_manufacturer(manuf_code)

    # Version (1 byte)
    result["Version"] = payload[6]

    # Meter Type (1 byte)
    medium_code = payload[7]
    medium_map = {
        0x03: "Electricity",
        0x04: "Heat",
        0x06: "Gas",
        0x07: "Water",
        0x21: "Heat (TKS specific)"
    }
    result["Meter Type"] = medium_map.get(medium_code, f"Unknown ({medium_code})")

    
    idx = 12  
    while idx < len(payload):
        DIF = payload[idx]
        idx += 1
        data_len = DIF & 0x0F 

        VIF = payload[idx]
        idx += 1

        description = None
        unit = None

        if VIF == 0x13:
            description = "Volume"
            unit = "m³"
        elif VIF == 0xFD: 
            if idx >= len(payload):
                description = "Manufacturer-specific (missing VIFE)"
                unit = "-"
            else:
                VIFE = payload[idx]
                idx += 1
                if VIFE == 0x17:
                    description = "Error Flags"
                    unit = "-"
                elif VIFE == 0x61:
                    description = "Cumulation Counter"
                    unit = "-"
                elif VIFE == 0x1F:
                    description = "Reserved"
                    unit = "-"
                else:
                    description = f"Manufacturer-specific (VIFE={VIFE:02X})"
        else:
            description = f"Unknown VIF {VIF:02X}"

        value_bytes = payload[idx:idx + data_len]
        idx += data_len
        value = int.from_bytes(value_bytes, byteorder="little")

        result["Data Records"].append({
            "Value": value,
            "Unit": unit,
            "Description": description
        })

    return result


def __main__():
    parsed = parse_mbus_payload()
    import pprint
    pprint.pprint(parsed)


if __name__ == "__main__":
    __main__()
