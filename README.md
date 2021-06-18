# Gateway_BLE_IoT

This repository provides a Python gateway framework to collect data from IoT devices using Bluetooth Low Energy.
Regarding hardware, this framework works with the nRF52840 dongle from Nordic Semiconductor.
The nRF52840 dongle should be flashed with connectivity_4.1.2_usb_with_s132_5.1.0.hex, which can be found in the directory: nrf52840_dongle.
This can be done with the application [nRF Connect for Desktop](https://www.nordicsemi.com/Software-and-tools/Development-Tools/nRF-Connect-for-desktop)

Furthermore, the framework has been tested with the [SensorTile](https://www.st.com/en/evaluation-tools/steval-stlkt01v1.html). 

## install 
`pip install blatann`  
`pip install pc-ble-driver-py` 
`pip install blatann`  

### Using with Windows

With the current version of `pc-ble-driver-py` there is an issue with USB latencies on Windows. The repo however has not been updated yet (per 21.05.21)  For Windows user it is recommended to replace the lib files in `\Lib\site-packages\pc_ble_driver_py\lib` with the content of this [.zip](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/3157.lib.zip) file.
Another way to resolve this is to basically replace the whole `pc-ble-driver-py` directory with the one provided in this repository.
More about this [issue](https://devzone.nordicsemi.com/f/nordic-q-a/74727/pc-ble-driver-py-throughput-limited-and-maximum-amount-of-peripherals)

### Using with macOS brew python
[Referring here](https://github.com/ThomasGerstenberg/blatann#using-with-macos-brew-python)

## Example how to use run.py:

```c
"""
Import statement
"""
import time
from setup import *


def main():

    ...

    ### Configure here to setup the nRF dongle ################
    config.port = "COM6"
    config.max_connected_peripherals = 4                     # Cannot open more than 5 with current setup, reduce queue sizes to increase that value
    config.vendor_specific_uuid_count = 20
    config.hardware_notification_queue_size = 16
    config.hardware_write_queue_size = 16
    config.attribute_table_size = 4096
    ###########################################################    

    ...
    ...

    ### Configure here to select devices and set parameters ###
    target_devices = ['P&SNode', 'CounterTester']

    connectionManager.set_default_connection_parameters(min_conn_interval_ms = 15,
                                                        max_conn_interval_ms = 15,
                                                        timeout_ms = 4000,
                                                        slave_latency = 0)
    ############################################################

    ...
    ...


    ### Configure here to filter characterics ###########
    dataCollector.set_all_writer_types("Writer")

    dataCollector.set_target_characteristic_on_device('P&SNode',['00020000-0001-11e1-ac36-0002a5d5c51b',
                                                                 '001d0000-0001-11e1-ac36-0002a5d5c51b'])

    dataCollector.set_target_characteristic_on_device('CounterTester', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a",
                                                                        "020013ac-4202-bcbc-eb11-43a172103324"])
    #####################################################

    ...


    """
    Measurement
    """
    measurement_max_duration = 300

    try:
        print("Wait {} seconds...".format(measurement_max_duration))
        time.sleep(measurement_max_duration)
        dataCollector.unsubscribe_all_devices()

    # Press CTRL + C to stop measurement.
    except KeyboardInterrupt:
        print("Stopping measurement...")
        dataCollector.unsubscribe_all_devices()    
```

After the measurement, the data received from the peripherals will be saved in the directory /data



