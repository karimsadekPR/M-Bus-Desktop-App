import serial
import time

def short_frame(control, addr):
    return bytes([0x10, control, addr, (control ^ addr) & 0xFF, 0x16])

def checksum_long(payload):
    return sum(payload) & 0xFF

def select_secondary_frame(id_bcd4, man=b'\xFF\xFF', ver=b'\xFF', med=b'\xFF'):
    payload = bytes([0x53, 0xFD, 0x52]) + id_bcd4 + man + ver + med
    L = len(payload)
    frame = bytes([0x68, L, L, 0x68]) + payload
    return frame + bytes([checksum_long(payload), 0x16])

def deselect(ser):
    ser.write(short_frame(0x40, 0xFD))
    ser.flush()
    time.sleep(0.05)
    ser.read_all()

def write_and_read(ser, tx, read_len=256, pause=0.25):
    ser.write(tx)
    ser.flush()
    time.sleep(pause)
    return ser.read(read_len)

def mask_str_to_bcd4(mask_str):
    """Convert 8-char hex nibble mask to 4-byte BCD, LSB-first."""
    nibbles = [int(x, 16) if x != 'F' else 0xF for x in mask_str]
    return bytes([
        ((nibbles[7] << 4) | nibbles[6]),
        ((nibbles[5] << 4) | nibbles[4]),
        ((nibbles[3] << 4) | nibbles[2]),
        ((nibbles[1] << 4) | nibbles[0])
    ])

def select_and_poll_mask(ser, id_bcd4):
    deselect(ser)
    sel = select_secondary_frame(id_bcd4)
    ack = write_and_read(ser, sel, read_len=1, pause=0.12)
    if ack != b'\xE5':
        return None
    rsp = write_and_read(ser, short_frame(0x5B, 0xFD), read_len=512, pause=0.4)
    if len(rsp) >= 15 and rsp[0] == 0x68:
        return rsp
    return None

def discover_secondary_addresses(port, baudrate=2400, parity=serial.PARITY_EVEN, timeout=1.0):
    found = []

    def search_mask(mask_str):
        # Send mask
        id_bcd4 = mask_str_to_bcd4(mask_str)
        rsp = select_and_poll_mask(ser, id_bcd4)

        if rsp is None:
            return  # no meter matches this mask

        # Count meters: In practice, collision detection is tricky.
        # For simplicity: if mask has no F → it's a full address match
        if 'F' not in mask_str:
            sec_addr = mask_str
            if sec_addr not in found:
                found.append(sec_addr)
            deselect(ser)
            return

        # Collision: refine by replacing first F with 0–9
        first_f_index = mask_str.index('F')
        for digit in '0123456789':
            new_mask = mask_str[:first_f_index] + digit + mask_str[first_f_index+1:]
            search_mask(new_mask)

    with serial.Serial(port=port, baudrate=baudrate,
                       bytesize=serial.EIGHTBITS, parity=parity,
                       stopbits=serial.STOPBITS_ONE, timeout=timeout) as ser:
        search_mask("FFFFFFFF")

    return found

addresses = discover_secondary_addresses("COM6", baudrate=2400)
print(addresses)
