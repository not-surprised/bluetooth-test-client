import sys
import math
import asyncio
import time

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.exc import BleakError


MANUFACTURER_DATA = {0xffff: b'$tZuFTNvsLGt9U^gsCM!t8$@Fd6'}

SERVICE_UUID      = '00000000-b1b6-417b-af10-da8b3de984be'
BRIGHTNESS_UUID   = '00000001-b1b6-417b-af10-da8b3de984be'
VOLUME_UUID       = '00000002-b1b6-417b-af10-da8b3de984be'
PAUSE_VOLUME_UUID = '10000001-b1b6-417b-af10-da8b3de984be'

LUX_TO_NITS = 1 / math.pi


def encode(string: str) -> bytes:
    return string.encode('utf-8')


def decode(byte_array: bytearray) -> str:
    return byte_array.decode('utf-8')


async def find_device() -> BLEDevice:
    print('Discovering devices...')
    async with BleakScanner() as scanner:

        start_time = time.time()
        future = asyncio.Future()
        detected = set()

        def detection_callback(device: BLEDevice, data: AdvertisementData):
            if device.address not in detected:
                detected.add(device.address)
                print(' ', device)
                if data.manufacturer_data == MANUFACTURER_DATA:
                    time_used = time.time() - start_time
                    print(f'Device found after {time_used:.2f} s')
                    future.set_result(device)

        scanner.register_detection_callback(detection_callback)
        return await future


async def find_device_debug() -> BLEDevice:
    discovered = set()
    print('Discovering devices...')
    number_of_scans = 0
    while True:
        number_of_scans += 1
        devices = await BleakScanner.discover(timeout=0.5)
        for device in devices:
            if device.address not in discovered:
                discovered.add(device.address)
                print(' ', device)
                try:
                    if device.metadata['manufacturer_data'][65535] == MANUFACTURER_UNIQUE_IDENTIFIER:
                        print(f'Device found after {number_of_scans} scans')
                        return device
                except KeyError:
                    pass
                except TypeError:
                    pass


async def test():
    device = await find_device()

    print(f'Connecting to device {device}')

    async with BleakClient(device, timeout=100) as client:
        # note: due to a bug in Windows connection will fail if we pair with the device
        #       so never try to pair with it
        services = await client.get_services()
        service = services.get_service(SERVICE_UUID)

        for c in service.characteristics:
            print()
            print(c.uuid, c.description)
            byte_array = await client.read_gatt_char(c)
            print('Read:', decode(byte_array))

            if c.uuid == PAUSE_VOLUME_UUID:
                print('Testing write')
                print('The previous read should give 0 and the next read should give 1')
                await client.write_gatt_char(c, encode('1'))
                print(decode(await client.read_gatt_char(c)))
                print('Finished testing write')

            elif c.uuid == BRIGHTNESS_UUID:

                def callback(sender: int, data: bytearray):
                    print(' ', f'Notified by {sender} with value {decode(data)}')

                print('Testing callback...')
                await client.start_notify(c, callback)
                await asyncio.sleep(3)
                await client.stop_notify(c)
                print('Finished testing callback')


if __name__ == '__main__':
    asyncio.run(test())
