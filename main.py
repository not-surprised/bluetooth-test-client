import sys

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

ADDRESS = (
    "B8:27:EB:6F:15:5B"
)

if len(sys.argv) == 2:
    ADDRESS = sys.argv[1]


SERVICE_UUID      = '00000000-b1b6-417b-af10-da8b3de984be'
BRIGHTNESS_UUID   = '00000001-b1b6-417b-af10-da8b3de984be'
VOLUME_UUID       = '00000002-b1b6-417b-af10-da8b3de984be'
PAUSE_VOLUME_UUID = '10000001-b1b6-417b-af10-da8b3de984be'
DESCRIPTOR_UUID   = '00002901-0000-1000-8000-00805f9b34fb'


async def print_services(ble_address: str):
    device = None
    while device is None:
        device = await BleakScanner.find_device_by_address(ble_address, timeout=2.0)

    async with BleakClient(device, timeout=100.0) as client:
        services = await client.get_services()
        print("Services:")
        for service in services:
            print(service)
        for service in services:
            if service.uuid == SERVICE_UUID:
                for characteristic in service.characteristics:
                    print()
                    print(characteristic.uuid, characteristic.description)
                    byte_array = await client.read_gatt_char(characteristic)
                    print(byte_array.decode("ascii"))


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(print_services(ADDRESS))
