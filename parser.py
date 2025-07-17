import struct
from datetime import datetime

def parse_packet(packet_bytes: bytes) -> dict:
    """
    Parse a 19-byte binary packet of sensor data.

    Format:
    - Bytes 0–1: Optical (big endian)
    - Bytes 2-3: Temperature (big endian)
    - Bytes 4-5: VOC 3 (big endian)
    - Bytes 6-7: VOC 2 (big endian)
    - Bytes 8-9: VOC 1 (big endian)
    - Bytes 10-11: CO2 (big endian)
    - Bytes 12-13: Humidity (used as capacitance)
    - Bytes 14-17: Timestamp (little endian, 4 bytes)
    - Byte 18: Patch ID
    """

    if len(packet_bytes) != 19:
        raise ValueError(f"Invalid packet length: expected 19 bytes, got {len(packet_bytes)}")

    optical = int.from_bytes(packet_bytes[0:2], byteorder='big')
    temperature = int.from_bytes(packet_bytes[2:4], byteorder='big')
    voc_3 = int.from_bytes(packet_bytes[4:6], byteorder='big')
    voc_2 = int.from_bytes(packet_bytes[6:8], byteorder='big')
    voc_1 = int.from_bytes(packet_bytes[8:10], byteorder='big')
    co2 = int.from_bytes(packet_bytes[10:12], byteorder='big')
    humidity = int.from_bytes(packet_bytes[12:14], byteorder='big')

    raw_timestamp = int.from_bytes(packet_bytes[14:18], byteorder='little')
    patch_id = packet_bytes[18]

    return {
        "timestamp": raw_timestamp,
        "patch_id": patch_id,
        "temperature_ohms": temperature,
        "voc_1_ohms": voc_1,
        "voc_2_ohms": voc_2,
        "voc_3_ohms": voc_3,
        "co2_ohms": co2,
        "optical_ohms": optical,
        "capacitance_raw": humidity,
    }