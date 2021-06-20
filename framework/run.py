"""
file name:			run.py
author:				Jackie Lim
created:			30. March 2021

brief:				This file the contains the main procedure from setting up the nRF Dongle, scanning and connecting to devices, subscribing to characteristics and saving them in a simple format in a csv file.
					The functions are documented in their respective definitions.

"""

"""
Import statement
"""
import time
from setup import *


def main():
	"""
	Configuration parameters for the nRF Dongle.
	"""
	config = ConfigurationParameter()


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


	"""
	Initialization of the nRF Dongle
	NOTE: 	If it raises pc_ble_driver_py.exceptions.NordicSemiException: Failed to ble_enable. Error code: NrfError.no_mem,
			try to reduce either number of maximum connected peripherals or queue sizes. 
			Reducing vendor_specific_uuid_count or attribute_table_size can help as well, although you should keep it high enough 
			to being able to properly discover your services.
	"""
	init = Setup(config)
	init.configure_and_open_device()
	"""
	Scanning other devices
	"""
	scanner = init.createScanner()
	scanner.scan_for_devices()
	scanner.show_scanned_devices()
	"""
	Connecting and handling peripheral devices
	"""
	connectionManager = scanner.createConnectionManager()


	###############################################################################
	### Configure here to set the target devices and connection intervals #########
	###############################################################################
	target_devices = ['P&SNode', 'CounterTester']
	# target_devices = ['CounterTester1','CounterTester2','CounterTester3',
	# 				  'CounterTester4','CounterTester5','CounterTester6',
	# 				  'CounterTester7','CounterTester8']

	connectionManager.set_default_connection_parameters(min_conn_interval_ms = 30,
														max_conn_interval_ms = 30,
														timeout_ms = 4000,
														slave_latency = 0)
	###############################################################################
	###############################################################################



	connectionManager.set_target_devices(target_devices)
	connectionManager.connect_with_all_target_devices()
	"""
	Collecting data from all connected peripherals
	"""
	dataCollector = connectionManager.create_collectorManager()
	dataCollector.show_base_dict_all()



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

	dataCollector.set_writers_for_all_devices()

	#########################################################################################
	### Configure here in case you want to write a value to a specific characteristic #######
	### Note that the characteristic is required to be writable!					  #######
	#########################################################################################

	dataCollector.write_characteristic('P&SNode', '00000001-000e-11e1-ac36-0002a5d5c51b', 1)

	#########################################################################################
	#########################################################################################



	"""
	Measurement
	"""
	#########################################################################################
	### Modify here to set the maximum measurement duration 				  ###############
	### One can stop the measurement before the duration by clicking CTRL + C ###############	
	#########################################################################################
	
	measurement_max_duration = 300

	#########################################################################################
	#########################################################################################

	dataCollector.subscribe_all_devices()
	try:
		print("Wait {} seconds...".format(measurement_max_duration))
		time.sleep(measurement_max_duration)
		dataCollector.unsubscribe_all_devices()

	# Press CTRL + C to stop measurement 
	except KeyboardInterrupt:
		print("Stopping measurement...")
		dataCollector.unsubscribe_all_devices()




if __name__ == "__main__":
	main()


