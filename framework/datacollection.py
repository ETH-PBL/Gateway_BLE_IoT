"""
file name:			datacollection.py
author:				Jackie Lim
created:			6. April 2021

brief:				This file contains classes which are responsible for setting up data collection of peripheral devices.
"""

"""
Import statement
"""
import timer
import customexception

from pathlib import Path
from datetime import datetime
from writer import *	

class Collector(object):
	"""
	Class corresponding to a single peripheral device. Contains GATT database of the peripheral.
	Will be instantiated if service discovery starts in CollectionManager.
	Contains multiple function for setting up the data collection for a single peripheral. 
	"""
	def __init__(self, name, database):
		"""
		INPUT PARAMETERS 

		param name: 	The name of the peer
		type name: 		str

		param database: The database of the corresponding peer
		type database: 	blatann.gatt.gattc.GattcDatabase
		"""
		self.name = name
		self.database = database

		self.base_dict = {}
		self.target_dict = {}
		self.target_characteristics = set()
		self.writer_list = []
		self.writer_type = 'PerfWriter'

		self.timestamp = 'n/a'
		self.offset = 0
		"""
		OTHER PARAMETERS

		param base_dict: 				The base dictionary which contains all READABLE and SUBSCRIBABLE characteristics.
		type base_dict: 				dict
										Format: {Service: {Characteristic UUID: Characteristic}}

		param target_dict:				The target dictionary which contains all charactersitics which are going to be subscribed to. Can be specified using the target_characteristics attribute
		type target_dict:				dict
										Format: {Service: {Characteristic UUID: Characteristic}}

		param target_characteristics:	A set of all characteristic which will be used as a filter for the base_dict to create the target_dict
		type target_characteristics:	set

		param writer_list: 				A list where each element is an instance of the Writer class for a single (READABLE & SUBSCRIBABLE) characteristic.
		type writer_list: 				list

		param writer_type:				The prefered type of the GenericWriter class. Per default: 'PerfWriter'
		type writer_type:				str

		param timestamp:				The timestamp when the measurement/subscription has begun.
		type timestamp:					str

		param offset:					The offset for PerfWriter. time.perf_counter() is relative to the time when the script runs.
		type offset:					float
		"""

	def __str__(self):
		return("Collector class of peripheral '{}'".format(self.name))

	def set_timestamp(self, arg_timestamp):
		"""
		Setter for timestamp when measuring data
		param arg_offset: Timestamp using datetime library
		type: float
		"""
		self.timestamp = arg_timestamp


	def set_offset(self, arg_offset):
		"""
		Setter for offset if using PerfWriter
		param arg_offset: The offset using time.perf_counter()
		type: float
		"""
		self.offset = arg_offset


	def show_database(self):
		"""
		Prints the whole database within the peer/connection, using blatanns database format.
		"""
		print(self.database)


	def get_subscribable_characteristics(self):
		"""
		Filters all subscribable characteristic of the database of a peripheral.

		Currently it filters all characteristic if it is READABLE and NOTIFIABLE!
		NOTE: One can change these condition by adjusting the "if(characteristic.subscribable is True and characteristic.readable is True)" condition in the dict comprehension.
		Using:
			characteristic.writable is (True or False)
			characteristic.notifiable is (True or False)
			characteristic.writable is (True or False)

		Format: {Service UUID: {Characteristic UUID: Characteristic}}
		"""

		print("Retrieving subscribable characteristics for device: '{}'...".format(self.name))
		temp_dict = {str(service.uuid): {str(characteristic.value_attribute.uuid): characteristic for characteristic in service.characteristics if (characteristic.subscribable is True and characteristic.readable is True)} for service in self.database.services}
		
		# Filter out all empty Services
		self.base_dict = {service: temp_dict[service] for service in temp_dict if bool(temp_dict[service]) is True}


	def show_base_dict(self):
		"""
		Shows the base dict of this Collector object
		"""
		print(self.base_dict)
	

	def show_target_dict(self):
		"""
		Shows the target dict of this Collector object
		"""
		print(self.target_dict)


	def _add_target_characteristics(self, arg_characteristic):
		"""
		Adds a target characteristic of this Collector object
		"""
		self.target_characteristics.add(arg_characteristic)


	def set_target_characteristics(self, arg_characteristic_list):
		"""
		Sets the target characteristic of this Collector object
		"""
		for characteristic in arg_characteristic_list:
			self._add_target_characteristics(characteristic) 


	def _apply_target_dict(self):
		"""
		Function which will instantiate the target dict attribute based on the target characteristic chosen by the user.
		"""

		# No specific target characteristics
		if len(self.target_characteristics) == 0:	
			self.target_dict = self.base_dict
		
		# With specific target characteristics
		else:
			temp_dict = {service_uuid: {characteristic_uuid: self.base_dict[service_uuid][characteristic_uuid] for characteristic_uuid in self.base_dict[service_uuid] if characteristic_uuid in self.target_characteristics} for service_uuid in self.base_dict}
			
			# Filter out empty services
			self.target_dict = {service: temp_dict[service] for service in temp_dict if bool(temp_dict[service]) is True}


	def clear_target_dict(self):
		"""
		Clears the target dictionary and the set of target characteristics
		"""
		self.target_dict = {}
		self.target_characteristics = set()

	
	def set_writer_type(self, arg_value):
		"""
		Sets the writer.GenericWriter class for this Collector object
		param arg_value:	The type of the Writer.
		type arg_value:		Currently: 'Writer', 'PerfWriter', 'PrinterWriter', 'CounterWriter', 'DummyWriter', 'ReadRequestWriter' are being supported.
		"""
		self.writer_type = arg_value


	def set_directories(self):
		"""
		Sets up all relevant directories for measuring data.
		Directory: /data/'Peripheral'/'Services'/'Characteristic_UUID'
		"""
		if self.writer_type == "PrinterWriter" or self.writer_type == "CounterWriter":
			return
		else:
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					Path(os.path.join('data', self.name, str(service), str(characteristic_uuid))).mkdir(exist_ok=True, parents=True)


	def set_writer_on_all_characteristics(self):
		"""
		Instantiates Writer classes determined by the writer_type and appends them into the self.writer_list list.
		"""
	
		if self.writer_type == 'Writer':
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					self.writer_list.append(Writer(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp))

		elif self.writer_type == 'PerfWriter':
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					self.writer_list.append(PerfWriter(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp, self.offset))
		
		elif self.writer_type == 'PrinterWriter':
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					self.writer_list.append(PrinterWriter(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp))

		elif self.writer_type == 'CounterWriter':
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					self.writer_list.append(CounterWriter(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp))

		elif self.writer_type == 'DummyWriter':
					for service in self.target_dict:
						for characteristic_uuid in self.target_dict[service].keys():
							self.writer_list.append(DummyWriter(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp))

		elif self.writer_type == 'ReadRequestWriter':
			for service in self.target_dict:
				for characteristic_uuid in self.target_dict[service].keys():
					self.writer_list.append(ReadRequestWriter(self.name, str(service), str(characteristic_uuid), self.target_dict[service][characteristic_uuid], self.timestamp))

		else:
			raise customexception.InputException("'{}' is not a valid Writer class.".format(self.writer_type))
			

	def write_characteristic(self, characteristic, value):
		"""
		Writes a specific value in the characteristic.

		param characteristic:	The selected characteristic
		type characteristic:	str
		param value:			The value to be written
		type value:				str or int
		"""
		status_found_characteristic = False
		for writer in self.writer_list:
			if characteristic == writer.characteristic_uuid:
				status_found_characteristic = True
				writer.write_characteristic(value)
		
		if status_found_characteristic is False:
			print("'{}' could not be found on device '{}'".format(characteristic, self.name))

	def subscribe_all_characteristic(self):
		"""
		Subscribes to all characteristic within the writer_list
		"""
		[writer.subscribe_to_characteristic() for writer in self.writer_list]

	def unsubscribe_all_characteristic(self):
		"""
		Unsubscribes to all Characteristics within the writer_list
		"""
		[writer.unsubscribe_to_characteristic() for writer in self.writer_list]
	

	def collector_comment(self, arg_comment):
		"""
		Function which is required to comment of the data.
		"""
		if self.writer_type == "PrinterWriter" or self.writer_type == "CounterWriter":
			return
		else:
			[writer.writer_comment(arg_comment) for writer in self.writer_list]


class CollectorManager(object):
	"""
	Class for handling the data collection of all peripheral devices
	"""
	def __init__(self, arg_connection_list):
		"""
		INPUT PARAMETERS 

		param collectors:	A list of all Collector classes, where each entry corresponds to a connection.
		type collectors: 	List with format ["Collector: collector"]
		"""
		self.connections = arg_connection_list

		self.collectors = {}	
		"""
		OTHER PARAMETERS

		param collectors: 	A dictionary with all Collector objects corresponding to all connected peripherals
		type collectors:	dict
							Format: {'Name': Collector}
		"""
		# Starting off with discovering all services and
		self._discover_all_services()
		self._get_subscribable_characteristics()

	"""
	Private functions
	"""
	def _discover_all_services(self):
		"""
		Discovers services from all connections. And sets up the Collector classes.
		"""
		[connection.discover_services() for connection in self.connections]
		self._set_collectors()


	def _set_collectors(self):
		"""
		Sets up all collectors in a dictionary with format {Name: Collector}
		"""
		self.collectors = {connection.name: connection.collector for connection in self.connections}


	def _get_subscribable_characteristics(self):
		"""
		Sets up all relevant (subscribable and readable) characteristic for each collector
		"""
		[self.collectors[name].get_subscribable_characteristics() for name in self.collectors]
	
	def _apply_all_target_dict(self):
		"""
		Applies the target dict on all connected peripherals based on the target_characteristics
		"""
		[self.collectors[name]._apply_target_dict() for name in self.collectors]

	def _set_all_directories(self):
		"""
		Sets up all directories for saving the data
		"""
		[self.collectors[name].set_directories() for name in self.collectors]

	def _show_target_dict_all(self):
		"""
		Shows the target dict of all devices
		"""
		print("################ TARGET CHARACTERISTICS #################")
		for name in self.collectors:
			print("### DEVICE: '{}' ###".format(self.collectors[name].name))
			self.collectors[name].show_target_dict()
		print("#########################################################")

	def _comment_data(self):
		"""
		In case user wants to comment the data.
		"""
		input_val = input("Comment: ")
		if input_val == '':
			return
		else:
			[self.collectors[name].collector_comment(input_val) for name in self.collectors]
	
	"""
	Public functions
	"""
	def set_target_characteristic_on_device(self, name, arg_characteristic_list):
		"""
		Function which allows to select specific characteristic from a peripheral device.

		param name: 					Name of the peripheral
		type name: 						str
		param arg_characteristic_list: 	A list with all specified characteristics
		type arg_characteristic_list: 	list with str elements		
		"""
		try:
			self.collectors[name].set_target_characteristics(arg_characteristic_list)
		except KeyError:
			print("Could not find Collector instance of peripheral '{}'".format(name))


	def show_base_dict_all(self):
		"""
		Shows the base dict of all devices.
		"""
		print("####### SUBSCRIBABLE AND READABLE CHARACTERISTICS #######")
		for name in self.collectors:
			print("### DEVICE: '{}' ###".format(self.collectors[name].name))
			self.collectors[name].show_base_dict()
		print("#########################################################")

	def show_base_dict_on_device(self, name):
		"""
		Shows the discovered base dict of the device.

		param name: 	Name of the peripheral
		type name: 		str		
		"""
		try:
			self.collectors[name].show_base_dict()
		except KeyError:
			print("Could not find Collector instance of peripheral '{}'".format(name))


	def set_all_writer_types(self, arg_type):
		"""
		Sets the type of the GenericWriter class. See writer.py
		Currently supports: 'Writer', 'PerfWriter', 'PrinterWriter', 'CounterWriter', 'DummyWriter', 'ReadRequestWriter'
		"""
		[self.collectors[name].set_writer_type(arg_type) for name in self.collectors]


	def set_writers_for_all_devices(self):
		"""
		Sets all directories and Writer classes within each Collector for all devices
		"""
		# Applying target dicts.
		self._apply_all_target_dict()

		# Show target dict before starting with the initialization of Writer classes.
		self._show_target_dict_all()

		# Asks for user input to confirm to start measurement.
		input_val = input("Continue with these characteristics? (y/n)")
		if input_val == 'n':
			raise customexception.UserException("Stopped by User")

		# Setting up all measurement directories. 
		self._set_all_directories()

		# Set the timestamp for all devices
		[self.collectors[name].set_timestamp(datetime.now().strftime("%d%m%y_%H%M%S")) for name in self.collectors]

		# Sets the offset in case we are using the PerfWriter
		temp_offset = time.perf_counter()
		[self.collectors[name].set_offset(temp_offset) for name in self.collectors]

		# Initiates Writer classes
		[self.collectors[name].set_writer_on_all_characteristics() for name in self.collectors]

	def write_characteristic(self, name, characteristic, value):
		"""
		Additional modification for Jean Megret's bachelor project.
		Write a value to a characteristic from a specific device

		param name: 			Name of the peripheral
		type name: 				str	
		param characteristic:	Name of the characteristic
		type characteristic:	str
		param value:			Value which is going to be written
		type value:				str or int
		"""
		try:
			self.collectors[name].write_characteristic(characteristic, value)
		except KeyError:
			print("Could not find Collector instance of peripheral '{}'".format(name))

	def subscribe_all_devices(self):
		"""
		Subscribes to all devices
		"""
		# Asks for user input to confirm to start measurement.
		input_val = input("Start measurement? (y/n)")
		if input_val == 'n':
			raise customexception.UserException("Stopped by User")


		[self.collectors[name].subscribe_all_characteristic() for name in self.collectors]

	def unsubscribe_all_devices(self):
		"""
		Unsubscribes to all devices
		"""
		[self.collectors[name].unsubscribe_all_characteristic() for name in self.collectors]
		
		# Comment the measurement
		self._comment_data()
	


		





### OLD ####################################################################

# def main():

# 	"""
# 	Using pathlib
# 	"""
# 	# Get the current directocry
# 	current_path = Path.cwd()
# 	print(current_path)

# 	# Check if the folder 'temp3' exists in the current directory
# 	print(Path('temp3').exists())

# 	# Create folder
# 	Path('temp3').mkdir(exist_ok=True)

# 	# Create subfolder
# 	c = "Test"
# 	Path(os.path.join('string','{}'.format(c))).mkdir(exist_ok=True, parents= True)

# 	"""
# 	csv import testing
# 	"""
# 	temp_time = datetime.now().strftime("%Y%m%d_%H%M%S")
# 	l = [1, 2, 3, 4, 5]
# 	s = [1,3,5,6,7]

# 	with open(os.path.join("temp3","temp1","{}.csv".format(temp_time)),'a', newline='') as file:
# 		writer = csv.writer(file)
# 		writer.writerow(l)
# 		writer.writerow(s)
		
		
# def main2():
# 	import random

# 	temp_time = datetime.now().strftime("%Y%m%d_%H%M%S")
# 	class TestClass(object):
# 		def __init__(self):
# 			self.var = 2
# 			self.write()

# 		def write(self):
# 			with open(os.path.join("temp","{}.csv".format(temp_time)),'a', newline='') as file:
# 				def generate_number():
# 					writer.writerow("Hello")

# 				writer = csv.writer(file)
# 				for i in range(5):
# 					generate_number()

# 	obj = TestClass()

# 	"""
# 	Goal is to create a directory with /Data/SensorName/Service/Characteristics/current_time_data.csv
# 	"""


# if __name__ == "__main__":
# 	main2()