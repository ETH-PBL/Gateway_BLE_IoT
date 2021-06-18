"""
file name:			setup.py
author:				Jackie Lim
created:			30. March 2021

brief:				This file contains classes which are responsible for setting up the nRF52840 Dongle from NordicSemiconductor with the proper parameters.
					This includes memory allocation for peripheral connections and queue sizes for notification and write request, etc.
"""

"""
Import statement
"""
import timer
import customexception
import constants
import time
import blatann
from scanner import Scanner


class ConfigurationParameter(object):
	"""
	Class for setting up required parameters before launching the nRF device. Contains relevant attributes, which the user can modify.
	The attributes will be used in the Setup class for configuring the nRF Device.
	"""
	def __init__(self):
		self._port = constants.DEFAULT_COM_PORT
		self._vendor_specific_uuid_count = constants.DEFAULT_NUMBER_CUSTOM_UUID
		self._max_connected_peripherals = constants.DEFAULT_NUMBER_PERIPHERALS
		self._hardware_notification_queue_size = constants.DEFAULT_HW_QUEUE_NOTIFICATION
		self._hardware_write_queue_size = constants.DEFAULT_HW_QUEUE_WRITE_COMMANDS
		self._attribute_table_size = constants.DEFAULT_ATTRIBUTE_TABLE_SIZE

		"""
		OTHER PARAMETERS 

		param _port: 								The port in which the nRF device is connected to (e.g. "COM4" or "/dev/ttyUSB0")
		type _port: 								str

		param _vendor_specific_uuid_count: 			The amount of vendor specific UUID the nRF device will allocate memory to. Increase this, if you have a lot of
													vendor specific uuid in the peripherals
		type _vendor_specific_uuid_count: 			int

		param _max_connected_peripherals: 			The maximum number of connected peripherals the nRF device can connect to. (Per default 5 if other parameters are not changed)
		type _max_connected_peripherals: 			int

		param _hardware_notification_queue_size: 	Hardware queue size used for notification which the nRF device needs to allocate memory to. 
												 	Decreasing this value will allow you to connect to more peripheral devices.
		type _hardware_notification_queue_size: 	int

		param _hardware_write_queue_size:			Hardware queue size used for writing commands which the nRF device need to allocate memory to.
													Decreasing this value will allow you to connect to more peripheral devices.
		type _hardware_write_queue_size:			int

		param _attribute_table_size:				The maximum size of the attribute table. Increase this if you have a lot of characteristics and services to discover.
		type _attribute_table_size:					int
		"""

	"""
	port setter and getter
	"""
	@property
	def port(self):
		return self._port

	@port.setter
	def port(self, arg_value):
		self._port = arg_value

	"""
	vendor_specific_uuid_count setter and getter
	"""	
	@property
	def vendor_specific_uuid_count(self):
		return self._vendor_specific_uuid_count
	
	@vendor_specific_uuid_count.setter
	def vendor_specific_uuid_count(self, arg_value):
		self._vendor_specific_uuid_count = arg_value
		
	"""
	max_connected_peripherals setter and getter
	"""
	@property
	def max_connected_peripherals(self):
		return self._max_connected_peripherals
	
	@max_connected_peripherals.setter
	def max_connected_peripherals(self, arg_value):
		self._max_connected_peripherals = arg_value

	"""
	hardware_write_queue_size setter and getter
	"""
	@property
	def hardware_write_queue_size(self):
		return self._hardware_write_queue_size

	@hardware_write_queue_size.setter
	def hardware_write_queue_size(self, arg_value):
		self._hardware_write_queue_size = arg_value

	"""
	hardware_notification_queue_size setter and getter
	"""
	@property
	def hardware_notification_queue_size(self):
		return self._hardware_notification_queue_size

	@hardware_notification_queue_size.setter
	def hardware_notification_queue_size(self, arg_value):
		self._hardware_notification_queue_size = arg_value

	"""
	attribute_table_size setter and getter
	"""
	@property
	def attribute_table_size(self):
		return self._attribute_table_size

	@attribute_table_size.setter
	def attribute_table_size(self, arg_value):
		self._attribute_table_size = arg_value

class Setup(object):
	""" 
	Main class for setting up the nRF dongle with the parameters from ConfigurationParameter
	"""

	def __init__(self, arg_parameters):
		"""
		INPUT PARAMETERS

		param arg_parameters:	The configuration parameters
		type arg_parameters:	ConfigurationParameter
		"""
		self.parameters = arg_parameters
		
		self.ble_device = None
		self.open_status = False
		"""
		OTHER PARAMETERS

		param ble_device: 	The BLE device. In this case the nRF Dongle.
		type ble_device: 	blatann.BleDevice

		param open_status: 	Attribute which returns True if the device has been opened.
		type open_status: 	boolean
		"""
	
	def __str__(self):
		if self.open_status is False:
			return("BLE device not opened yet")
		if self.open_status is True:
			return("BLE device at port: '{}'".format(self.parameters.port))

	"""
	Public functions
	"""

	def configure_and_open_device(self):
		"""
		Sets up the nRF Device with the corresponding ConfigurationParameter object and opens it.
		exceptions: 
			raises pc_ble_driver_py.exceptions.NordicSemiException: Failed to open. Error code: NrfError.rpc_h5_transport_state:
				The nRF Dongle has not been detected: Which happens if the wrong port has been configured or the nRF Dongle has not been flashed yet.
			
			raises pc_ble_driver_py.exceptions.NordicSemiException: Failed to ble_enable. Error code: NrfError.no_mem:
				The nRF Dongle has not enough memory space to allocate. Reducing the notification & write_commands queue sizes, 
				vendor_specific_uuid_count or the maximum number of peripherals can avoid this exception.
		"""
		
		print("Opening nRF Device...")
		self.ble_device = blatann.BleDevice(self.parameters.port,
											notification_hw_queue_size = self.parameters.hardware_notification_queue_size,
											write_command_hw_queue_size = self.parameters.hardware_write_queue_size,
											)

		self.ble_device.configure(vendor_specific_uuid_count = self.parameters.vendor_specific_uuid_count,
								  max_connected_peripherals = self.parameters.max_connected_peripherals,
								  max_secured_peripherals = 0,
								  max_connected_clients = 0,
								  attribute_table_size= self.parameters.attribute_table_size
								  )

		self.ble_device.open()
		print("Successfully openend nRF Device.")
		self.open_status = True


	def close_device(self):
		"""
		Closes the nRF device
		"""
		if self.open_status == True:
			print("Closing nRF Device...")
			self.ble_device.close()
			print("Successfully closed Device.")
			self.open_status = False
			# time.sleep(3)
		else:
			print("no nRF device has been opened yet")



	def createScanner(self):
		"""
		Returns an object of the scanner.Scanner class with the corresponding nRF Device. The scanner.Scanner class will handle tasks related to scanning peripheral devices.
		"""
		if self.open_status is not True:
			raise customexception.InvalidStateException("Cannot instantiate Scanner class if no nRF device has been opened yet.")
		return Scanner(self.ble_device)



def example():
	par = ConfigurationParameter()
	par.hardware_write_queue_size = 14
	print(par.hardware_notification_queue_size)
	print(par.hardware_write_queue_size)
	
	setup = Setup(par)
	scan = setup.createScanner()	# Should raise exception


if __name__ == "__main__":
	example()