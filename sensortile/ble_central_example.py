#!/bin/python

import struct
from blatann import BleDevice
from blatann.uuid import Uuid128

counter1 = []
counter2 = []

def on_counter1_char_notification(characteristic, event_args):
    counter = struct.unpack("<I", event_args.value)
    counter2.append(counter)

def on_counter2_char_notification(characteristic, event_args):
    counter = struct.unpack("<I", event_args.value)
    counter1.append(counter)

DEVICE = "CounterTester"

ble_device = BleDevice("/dev/ttyACM1")
ble_device.configure(vendor_specific_uuid_count=20, attribute_table_size=4096)
ble_device.open()

ble_device.scanner.set_default_scan_params(timeout_seconds=4)

scan_report = ble_device.scanner.start_scan().wait()

target_address = None

for report in scan_report.advertising_peers_found:
    if report.device_name == DEVICE:
        target_address = report.peer_address
        print("Found \"%s\" at address \"%s\"" % (DEVICE, target_address))
        break

if not target_address:
    print("Could not find \"s\"" % DEVICE)
    exit()

peer = ble_device.connect(target_address).wait()
if not peer:
    print("Could not connect to target")
    exit()

print("Connected to target!")
_, event_args = peer.discover_services().wait(10, exception_on_timeout=False)
print("Discovered serivces")
for service in peer.database.services:
    print("Service: %s" % service)

counter1_characteristic = peer.database.find_characteristic(Uuid128("020013ac-4202-bcbc-eb11-43a172103324"))
counter2_characteristic = peer.database.find_characteristic(Uuid128("020013ac-4202-bcbc-eb11-43a172103325"))

if not counter1_characteristic:
    print("Counter 1 Characteristic not found")
    exit()

if not counter2_characteristic:
    print("Counter 2 Characteristic not found")
    exit()

counter1_characteristic.subscribe(on_counter1_char_notification).wait(5)
counter2_characteristic.subscribe(on_counter2_char_notification).wait(5)
try:
    while True:
        pass
except KeyboardInterrupt:
    peer.disconnect().wait()
    ble_device.close()
