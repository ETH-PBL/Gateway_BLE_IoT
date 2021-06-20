# Gateway_BLE_IoT

This repository provides a Python gateway framework to collect data from IoT devices using Bluetooth Low Energy.
Regarding hardware, this framework works with the [nRF52840 dongle](https://www.nordicsemi.com/Software-and-tools/Development-Kits/nRF52840-Dongle) from Nordic Semiconductor.
The nRF52840 dongle should be flashed with connectivity_4.1.2_usb_with_s132_5.1.0.hex, which can be found in the directory: nrf52840_dongle.
This can be done with the application [nRF Connect for Desktop](https://www.nordicsemi.com/Software-and-tools/Development-Tools/nRF-Connect-for-desktop)

Furthermore, the framework has been tested with the [SensorTile](https://www.st.com/en/evaluation-tools/steval-stlkt01v1.html). The firmware for the SensorTile is written
in C and has been implemented using [STMCube32IDE](https://www.st.com/en/development-tools/stm32cubeide.html).

## install 
`pip install blatann`  
`pip install pc-ble-driver-py` 
`pip install blatann`  

### Using with Windows

With the current version of `pc-ble-driver-py` there is an issue with USB latencies on Windows. The library however has not been updated yet (per 21.05.21)  For Windows user it is recommended to replace the lib files in `\Lib\site-packages\pc_ble_driver_py\lib` with the content of this [.zip](https://devzone.nordicsemi.com/cfs-file/__key/communityserver-discussions-components-files/4/3157.lib.zip) file.
Another way to resolve this is to basically replace the whole `pc-ble-driver-py` directory with the one provided in this repository.
More about this [issue](https://devzone.nordicsemi.com/f/nordic-q-a/74727/pc-ble-driver-py-throughput-limited-and-maximum-amount-of-peripherals)

### Using with macOS brew python
[Referring here](https://github.com/ThomasGerstenberg/blatann#using-with-macos-brew-python)

## Example how to use /framework/run.py:

```c
"""
Import statement
"""
import time
from setup import *


def main():

    ...

    #####################################################
    ### Configure here to set up the nRF52840 dongle ####
    #####################################################
    config.port = "COM6"
    config.max_connected_peripherals = 8                     
    config.vendor_specific_uuid_count = 20
    config.hardware_notification_queue_size = 4
    config.hardware_write_queue_size = 4
    config.attribute_table_size = 4096
    #####################################################
    #####################################################

    ...
    ...

    ###############################################################################
    ### Configure here to set the target devices and connection intervals #########
    ###############################################################################
    target_devices = ['P&SNode', 'CounterTester']
    # target_devices = ['CounterTester1','CounterTester2','CounterTester3',
    #                 'CounterTester4','CounterTester5','CounterTester6',
    #                 'CounterTester7','CounterTester8']

    connectionManager.set_default_connection_parameters(min_conn_interval_ms = 30,
                                                        max_conn_interval_ms = 30,
                                                        timeout_ms = 4000,
                                                        slave_latency = 0)
    ###############################################################################
    ###############################################################################

    ...
    ...

    #################################################################################################################
    ### Configure here to select which Writer you want to use and which characteristic datas you want to collect ####
    #################################################################################################################
    dataCollector.set_all_writer_types("PerfWriter")
    dataCollector.set_target_characteristic_on_device('P&SNode',['00020000-0001-11e1-ac36-0002a5d5c51b',
                                                                 '001d0000-0001-11e1-ac36-0002a5d5c51b'])

    # dataCollector.set_target_characteristic_on_device('CounterTester', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester1', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester2', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester3', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester4', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester5', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester6', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester7', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])
    # dataCollector.set_target_characteristic_on_device('CounterTester8', ["ad4a4041-5562-4112-9aa8-0aa23d0ce57a"])

    #################################################################################################################
    #################################################################################################################

    ...
    #########################################################################################
    ### Configure here in case you want to write a value to a specific characteristic #######
    ### Note that the characteristic is required to be writable!                      #######
    #########################################################################################

    dataCollector.write_characteristic('P&SNode', '00000001-000e-11e1-ac36-0002a5d5c51b', 1)

    #########################################################################################
    #########################################################################################
    
    
    """
    Measurement
    """
    #########################################################################################
    ### Modify here to set the maximum measurement duration                   ###############
    ### One can stop the measurement before the duration by clicking CTRL + C ###############   
    #########################################################################################
    
    measurement_max_duration = 300

    #########################################################################################
    #########################################################################################

    try:
        print("Wait {} seconds...".format(measurement_max_duration))
        time.sleep(measurement_max_duration)
        dataCollector.unsubscribe_all_devices()

    # Press CTRL + C to stop measurement.
    except KeyboardInterrupt:
        print("Stopping measurement...")
        dataCollector.unsubscribe_all_devices()    
```

After the measurement, the data received from the peripherals will be saved in the subdirectory /data. This subdirectory will be saved in the directory, where you are launching the run.py script.



