# ble_receiver.py

"""
Supports:
* Multi-patch connection
* Initial scan period
* Periodic rescanning for late or reconnected devices
"""
import asyncio
import bleak
from bleak import BleakClient, BleakScanner
from parser import parse_packet
from logger import BufferedLogger

SERVICE_UUID = bleak.uuids.normalize_uuid_str("1234")
CHAR_UUID = bleak.uuids.normalize_uuid_str("1234")
BLE_SCAN_TIMEOUT = 5
# DEVICE_NAME_PREFIXES = ["AirPatch", "APCH", "APCH_01", "APCH_00"]
prefix_filter = ("airpatch", "apch")
logger = BufferedLogger(buffer_size=1)
connected_addresses = set()

async def handle_notification(sender, data):
    try:
        parsed = parse_packet(data)
        print(f"[{parsed['patch_id']}] Packet: {parsed}")
        logger.log(parsed)
    except Exception as e:
        print(f"Parse error: {e}")

async def connect_to_patch(device):
    client = BleakClient(device)
    if device.address in connected_addresses:
        return
    try:
        await client.connect()
        print(f"Connected to {device.name} at {device.address}")

        # services = await client.get_services()
        # print(services)
        # for service in services:
        #     print(f"Service: {service}, UUID: {service.uuid}")
        #     if service.uuid is "1234":
        #         chars = service.characteristics
        #         for char in chars:
        #             if char.uuid is "1234":
        #

        await client.start_notify(CHAR_UUID, handle_notification)
        print("Subscribed to characteristic");
        connected_addresses.add(device.address)

        while True:
            await asyncio.sleep(1)  # Keep alive

    except Exception as e:
        print(f"Failed to connect to {device.name} ({device.address}): {e}")
        await client.disconnect()

async def initial_scan_and_connect(scan_duration=10):
    print(f"Scanning for patches for {scan_duration} seconds...")
    # await asyncio.sleep(scan_duration)  # Let nearby patches boot
    devices = await BleakScanner.discover(timeout=scan_duration)
    targets = [
        d for d in devices
        if d.name and d.name.lower().startswith(prefix_filter)
    ]

    print(f"Found {len(devices)} total devices.")
    for t in targets:
        print(f"Target: {t.name} ({t.address})")

    tasks = [asyncio.create_task(connect_to_patch(d)) for d in targets]
    return tasks

async def periodic_rescan(interval=5):
    while True:
        await asyncio.sleep(interval)
        print("Rescanning for new patches...")
        devices = await BleakScanner.discover(timeout=BLE_SCAN_TIMEOUT)
        new_targets = [
            d for d in devices
            if d.name and d.name.lower().startswith(prefix_filter)
            and d.address not in connected_addresses
        ]

        for d in new_targets:
            print(f"New patch found: {d.name} ({d.address})")
            asyncio.create_task(connect_to_patch(d))

async def main():
    # Start initial connect
    init_tasks = await initial_scan_and_connect(scan_duration=BLE_SCAN_TIMEOUT)

    # Schedule periodic rescans
    periodic_task = asyncio.create_task(periodic_rescan(interval=5))

    # Gather all tasks and a never-ending sleep to prevent exit
    await asyncio.gather(
        *init_tasks,
        periodic_task,
        asyncio.Event().wait()  # Run indefinitely
    )

if __name__ == "__main__":
    asyncio.run(main())
