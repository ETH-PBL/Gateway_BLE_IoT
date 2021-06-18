"""
file name:			connection.py
author:				Jackie Lim
created:			6. April 2021

brief:				This file contains classes which are responsible for configuring, estalishing and maintaining connections with peripheral devices.
"""

"""
Import statement
"""
import timer
import customexception
import constants

from datacollection import *
from blatann.peer import ConnectionParameters

class Connection(object):
	"""
	Class which corresponds to a single connection with a peripheral. 
	"""
	def __init__(self, arg_peer):
		"""
		INPUT PARAMETERS

		param arg_peer: 	The connection/peer corresponding the peripheral
		type arg_peer:		blatann.peer.Peer
		"""
		self.peer = arg_peer

		self.name = self.peer.name
		self.discovered = False
		self._collector = None

		"""
		OTHER PARAMETERS:

		param name: 		The name of the peripheral
		type name: 			str

		param discovered: 	Attribute which tells whether the database of this connection has been discovered
		type discovered: 	boolean

		param _collector: 	The Collector object of this connection
		type _collector: 	datacollection.Collector
		"""

	def __str__(self):
		return("Connection class corresponding peripheral: '{}'".format(self.name)) 

	def disconnect(self):
		"""
		Disconnects this peer connection
		"""
		if self.status is True:
			self.peer.disconnect()
			print("Disconnected from '{}'.".format(self.peer.name))
		return
	
	@property
	def this_connection(self):
		"""
		Returns this Connection object class
		"""
		return self

	@property
	def status(self):
		"""
		Returns boolean whether the corresponding peripheral is connected to the nRF device. True if it is still connected.
		"""
		return self.peer.connected
	

	"""
	collector setter and getter
	"""	
	@property
	def collector(self):
		return self._collector
	
	@collector.setter
	def collector(self, arg_value):
		self._collector = arg_value


	def discover_services(self):
		"""
		Discover services which the current connection offers. peer.database will be updated.
		Note: If called more than once, the database will be extended with the same values as before
		"""
		if self.discovered is True:
			print("Device '{}' has already discovered.".format(self.name))
			return
		else:	
			print("Discover Services...")
			_, event_args = self.peer.discover_services().wait(10, exception_on_timeout=False)
			print("Service discovery for peripheral '{}' complete!".format(self.name))

			# Instantiates the Collector class with the database and reference it with attribute self._collector
			self.collector = Collector(self.name, self.peer.database)
			self.discovered = True


class ConnectionManager(object):
	"""
	Main Class for maintaining and handling all connections with peripherals.
	"""

	def __init__(self, arg_ble_device, arg_scan_report_dict):
		"""
		INPUT PARAMETERS 

		param	arg_ble_device: The ble_device operating
		type	arg_ble_device: blatann.device.BleDevice
		param	arg_scan_report_dict: The formatted collection of all scanned nearby devices.
		type	arg_scan_report_dict: Dict with format: {"str:Name": Address}
		"""
		self.ble_device = arg_ble_device
		self.scan_report_dict = arg_scan_report_dict

		self.target_devices = set()							
		self.connections = []		
		self.connection_parameter = ConnectionParameters(constants.DEFAULT_MIN_CONN_INT_MS, constants.DEFAULT_MAX_CONN_INT_MS, constants.DEFAULT_TIMEOUT_MS, constants.DEFAULT_SLAVE_LATENCY)
			
		"""
		OTHER PARAMETERS

		param target_devices:		A set which contains all name of target devices		
		type target_devices:		set

		param connections:			List which contains Connections object
		type connections:			list
		
		param connection_parameter:	The default connection parameter
		type connection_parameter:	blatann.peer.ConnectionParameters
		"""

	def __str__(self):
		return("ConnectionManager class of: '{}'".format(self.ble_device)) 

	def __del__(self):
		if self.ble_device.ble_driver.is_open is False:
			return
		else:
			self.disconnect_all()

	"""
	Private function
	"""
	
	def _add_target_device(self, arg_target_device):
		"""
		Appends a target device to the list
		
		param arg_target_device: Target device
		type arg_target_device: str
		"""
		self.target_devices.add(arg_target_device)

	def _connect_to(self, arg_target_name, arg_target_address):
		"""
		Connects the nRF device with the respective peripheral
		param arg_target_name: 		The name of the target device
		type arg_target_name: 		str
		param arg_target_address: 	The address of the corresponding target device
		type arg_target_address: 	blatann.BLEAddr
		returns: 					the peer of the corresponding connection (blatann.peer.Peer)
		"""
		# NOTE: arg_target_name might not necessarily be the same as peer.name. If that is the case, adjust restore_connections: 
		#		- Replace peer.name with target_name from the scan_report_dict
		
		print("Connecting to '{}'...".format(str(arg_target_name)))
		peer = self.ble_device.connect(arg_target_address, self.connection_parameter).wait(5)
		print("Successfully connected to '{}'".format(str(peer.name)))
		return peer

	"""
	Public functions
	"""

	def disconnect_all(self):
		"""
		Disconnects all peripherals
		"""
		[connection.disconnect() for connection in self.connections]
		self.connections.clear()


	def show_target_devices(self):
		"""
		Prints all target devices
		"""
		print(self.target_devices)


	def set_target_devices(self, arg_list_target_devices):
		"""
		Set all devices which the nRF device should connect to.
		
		param arg_list_target_devices: Target devices
		type arg_list_target_devices: list with str elements
		"""
		for target_device in arg_list_target_devices:
			self._add_target_device(target_device)
	

	def clear_target_devices(self):
		"""
		Clears the selected target devices
		"""
		self.target_devices = set()


	def set_default_connection_parameters(self, min_conn_interval_ms = constants.DEFAULT_MIN_CONN_INT_MS, max_conn_interval_ms = constants.DEFAULT_MAX_CONN_INT_MS, timeout_ms = constants.DEFAULT_TIMEOUT_MS, slave_latency = constants.DEFAULT_SLAVE_LATENCY):
		"""
		Sets the preferred connection parameters which are going to be negotiated with the peripherals
		
		NOTE: 	Use it before establishing connections.
		
		NOTE: 	With multiple devices, it is esssential to have proper tuned parameters.
				In this case it is recommended to use: (7.5 * (Number of peripherals)) ms as the connection interval (for both min_conn_interval_ms and max_conn_interval_ms),
				since the event length corresponds to 7.5ms. 
				See ref: https://github.com/ThomasGerstenberg/blatann/issues/78 

		param min_conn_interval_ms:		The minimum connection interval the central negotiates with the peripherals, in milliseconds, at least 7ms, has to be a multiple of 1.25ms
		param max_conn_interval_ms:		The maximum connection interval the central negotiates with the peripherals, in milliseconds, at most 4000ms, has to be a multiple of 1.25ms
		param timeout_ms:				The connection timeout, in ms. Has to be a multiple of 10ms
		param slave_latency:			The slave latency, how many connection events the peripheral is allowed to skip. Has to be a value between 0 and 499
		"""
		self.connection_parameter = ConnectionParameters(min_conn_interval_ms, max_conn_interval_ms, timeout_ms, slave_latency)


	def connect_with_all_target_devices(self):
		"""
		Connects with all devices selected and stored in self.target_devices.
		The connections will be saved in a list in attribute self.connections
		"""
		if len(self.target_devices) == 0:
			raise customexception.InputException("No target devices selected")

		for target_name in self.target_devices:
			try:
				self.connections.append(Connection(self._connect_to(target_name, self.scan_report_dict[target_name])))
			except KeyError:
				print("Could not find '{}' in the scan report".format(target_name))
				input_value = input("Continue? (y/n)")
				if input_value == 'n':
					raise customexception.UserException("Stopped by User")
				else:
					continue


	def restore_connections(self):
		"""
		Iterates and checks through all connection and reestablish them if disconnected. Not fully tested yet.
		Would NOT recommend to restore connections in general or else the central scheduling will be a mess. The central will have a hard time re-scheduling all connections.
		
		NOTE: connection_name does not necessarily be the same as target_name from self.connect_with_all_devices
		"""
		self.connections[:] = [Connection(self._connect_to(connection.name, self.scan_report_dict[connection.name])) if connection.status is False else connection for connection in self.connections]


	def show_connected_devices(self):
		"""
		Print all connected devices in self.connections
		"""
		[print("connections[{}]: '{}'".format(self.connections.index(connection), connection.name)) for connection in self.connections]
	

	def create_collectorManager(self):
		"""
		Creates an datacollection.CollectorManager class from the current connections
		exception: If no devices have been connected yet, raises InvalidStateException
		"""
		if len(self.connections) == 0:
			raise customexception.InvalidStateException("Cannot create CollectorManager if no devices are connected")

		else:
			return CollectorManager(self.connections)



	# NOTE: To the following function: It will generally slow all BLE event. Has to be done before connecting to devices
	# It will mess up the whole central scheduling.

	# def set_connection_parameters_to_device(self, peripheral, min_conn_interval_ms = constants.DEFAULT_MIN_CONN_INT_MS , max_conn_interval_ms = constants.DEFAULT_MAX_CONN_INT_MS, timeout_ms = constants.DEFAULT_TIMEOUT_MS, slave_latency = constants.DEFAULT_SLAVE_LATENCY):
	# 	"""
	# 	Sets the preferred connection parameters which are going to be negotiated with the peripherals
	# 	NOTE: Use it after establishing connection with a peripheral

	# 	param peripheral: 				The name of the peripheral
	# 	param min_conn_interval_ms:		The minimum connection interval the central negotiates with the peripherals, in milliseconds, at least 7ms, has to be a multiple of 1.25ms
	# 	param max_conn_interval_ms:		The maximum connection interval the central negotiates with the peripherals, in milliseconds, at most 4000ms, has to be a multiple of 1.25ms
	# 	param timeout_ms:				The connection timeout, in ms. Has to be a multiple of 10ms
	# 	param slave_latency:			The slave latency, how many connection events the peripheral is allowed to skip. Has to be a value between 0 and 499
	# 	"""
	# 	if len(self.connections) == 0:
	# 		raise customexception.InputException("No devices are connected yet")

	# 	status_found = False
	# 	for connection in self.connections:
	# 		if peripheral != connection.name:
	# 			continue
	# 		else:
	# 			status_found = True
	# 			connection.peer.set_connection_parameters(min_conn_interval_ms, max_conn_interval_ms, timeout_ms, slave_latency)
	# 			time.sleep(0.1)
	# 			break

	# 	if status_found is False:
	# 		print("Device '{}' not connected".format(peripheral))	
	
	
	# NOTE: To the following function: It will generally slow all BLE event. Has to be done before connecting to devices
	# It will mess up the whole central scheduling.

	# 	# def set_recommended_connection_parameter(self):
	# 	"""
	# 	Sets the recommended connection parameters which are going to be negotiated with the peripherals. Recommended if connecting with multiple devices
	# 	The length of a single connection event seems to be 7.5ms. Therefore we are multiplying the number of peripheral to reduce the probability of a collision of 2 peripheral packet arrival.
	# 	See: https://infocenter.nordicsemi.com/index.jsp?topic=%2Fsds_s132%2FSDS%2Fs1xx%2Fmultilink_scheduling%2Fmultilink_scheduling.html
	# 	NOTE: Use it after establishing connection with peripherals
	# 	"""
	# 	if len(self.connections) == 0:
	# 		raise customexception.InputException("No devices are connected yet")
		
	# 	interval_ms = len(self.connections) * 7.5

	# 	for connection in self.connections:
	# 		connection.peer.set_connection_parameters(interval_ms, interval_ms, constants.DEFAULT_TIMEOUT_MS, constants.DEFAULT_SLAVE_LATENCY)
		
	# 	time.sleep(1)



	# """
	# Temporary functions for debugging purposes
	# """
	# def temp_print_type(self):
	# 	for target in self.target_devices:
	# 		print("{}: {}".format(target, type(target)))
	# 		print("{}: {}".format(self.target_devices[target], type(self.target_devices[target])))