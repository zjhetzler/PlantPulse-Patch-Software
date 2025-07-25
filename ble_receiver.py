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
prefix_filter = ("airpatch", "apch")
logger = BufferedLogger(buffer_size=1)
connected_addresses = dict()

async def handle_notification(sender, data):
    try:
        parsed = parse_packet(data)
        print(f"[{parsed['patch_id']}] Packet: {parsed}")
        logger.log(parsed)
    except Exception as e:
        print(f"Parse error: {e}")

def disconnect_callback(sender: BleakClient):
    print(f"Patch {connected_addresses[sender.address]} disconnected")
    connected_addresses.pop(sender.address)
    print(connected_addresses)

async def connect_to_patch(device):
    client = BleakClient(device, disconnected_callback=disconnect_callback)
    if device.address in connected_addresses:
        return

    connected_addresses[device.address] = device.name

    try:
        await client.connect()
        print(f"Connected to {device.name} at {device.address}")

        await client.start_notify(CHAR_UUID, handle_notification)
        print("Subscribed to characteristic")
        print(connected_addresses)

    except Exception as e:
        print(f"Failed to connect to {device.name} ({device.address}): {e}")
        if client.is_connected:
            await client.disconnect()
        if client.address in connected_addresses:
            connected_addresses.pop(client.address)

async def scan_and_connect(scan_duration=10):
    while True:
        print(f"Scanning for patches for {scan_duration} seconds...")
        # await asyncio.sleep(scan_duration)  # Let nearby patches boot
        devices = await BleakScanner.discover(timeout=scan_duration)
        targets = [
            d for d in devices
            if d.name and d.name.lower().startswith(prefix_filter)
               and d.address not in connected_addresses
        ]

        # print(f"Found {len(devices)} total devices.")
        for t in targets:
            print(f"Patch found: {t.name} ({t.address})")
            asyncio.create_task(connect_to_patch(t))


        # tasks = [asyncio.create_task(connect_to_patch(d)) for d in targets]
        # return tasks

async def main():

    # Schedule periodic rescans
    periodic_task = asyncio.create_task(scan_and_connect(scan_duration=BLE_SCAN_TIMEOUT))
    # Gather all tasks and a never-ending sleep to prevent exit
    await asyncio.gather(
        periodic_task,
        asyncio.Event().wait()  # Run indefinitely
    )

if __name__ == "__main__":
    asyncio.run(main())
