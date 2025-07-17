# ble_receiver.py

"""
Supports:
* Multi-patch connection
* Initial scan period
* Periodic rescanning for late or reconnected devices
"""

import asyncio
from bleak import BleakClient, BleakScanner
from parser import parse_packet
from logger import BufferedLogger

SERVICE_UUID = "1234"
CHAR_UUID = "1234"
DEVICE_NAME_PREFIXES = ["AirPatch", "APCH", "APCH_01", "APCH_00"]

logger = BufferedLogger(buffer_size=10)
connected_addresses = set()

async def handle_notification(sender, data):
    try:
        parsed = parse_packet(data)
        print(f"[{parsed['patch_id']}] Packet: {parsed}")
        logger.log(parsed)
    except Exception as e:
        print(f"Parse error: {e}")

async def connect_to_patch(device):
    if device.address in connected_addresses:
        return
    try:
        client = BleakClient(device)
        await client.connect()
        await client.start_notify(CHAR_UUID, handle_notification)
        print(f"Connected to {device.name} at {device.address}")
        connected_addresses.add(device.address)

        while True:
            await asyncio.sleep(1)  # Keep alive

    except Exception as e:
        print(f"Failed to connect to {device.name} ({device.address}): {e}")

async def initial_scan_and_connect(scan_duration=10):
    print(f"Scanning for patches for {scan_duration} seconds...")
    await asyncio.sleep(scan_duration)  # Let nearby patches boot
    devices = await BleakScanner.discover()
    targets = [
        d for d in devices
        if d.name and any(p in d.name for p in DEVICE_NAME_PREFIXES)
    ]

    print(f"Found {len(devices)} total devices.")
    for t in targets:
        print(f"Target: {t.name} ({t.address})")

    tasks = [asyncio.create_task(connect_to_patch(d)) for d in targets]
    return tasks

async def periodic_rescan(interval=30):
    while True:
        await asyncio.sleep(interval)
        print("Rescanning for new patches...")
        devices = await BleakScanner.discover()
        new_targets = [
            d for d in devices
            if d.name and any(p in d.name for p in DEVICE_NAME_PREFIXES)
            and d.address not in connected_addresses
        ]

        for d in new_targets:
            print(f"New patch found: {d.name} ({d.address})")
            asyncio.create_task(connect_to_patch(d))

async def main():
    # Start initial connect
    init_tasks = await initial_scan_and_connect(scan_duration=5)

    # Schedule periodic rescans
    periodic_task = asyncio.create_task(periodic_rescan(interval=30))

    # Gather all tasks and a never-ending sleep to prevent exit
    await asyncio.gather(
        *init_tasks,
        periodic_task,
        asyncio.Event().wait()  # Run indefinitely
    )

if __name__ == "__main__":
    asyncio.run(main())
