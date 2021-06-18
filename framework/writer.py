"""
file name:			writer.py
author:				Jackie Lim
created:			5. May 2021

brief:				This file contains classes which are responsible for acquiring and processing data from the peripherals.
"""

"""
Import statement
"""
import timer
import customexception
import os
import csv
import time
import struct

class GenericWriter(object):
	"""
	Base class for all other Writer. Writers are classes which are responsible for acquiring notification for a single characteristic.
	Contains all basic attributes for setting up the acquisition of data.
	"""
	
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		"""
		INPUT PARAMETERS

		param arg_name: 		Name of the device
		type arg_name:			str

		param arg_service: 		Service of the characteristic
		type arg_service: 		str

		param arg_cha_uuid: 	The UUID of the characteristic
		type arg_cha_uuid: 		str

		param arg_cha: 			The characteristic itself
		type arg_cha: 			blatann.gatt.gattc.GattcCharacteristic

		param arg_time: 		The time when the Writers are instantiated
		type arg_time: 			str
								Format: e.g. '030821_081500' corresponds to 03. August 2021 at 08:15:00
		"""
		self.name = arg_name
		self.service = arg_service
		self.characteristic_uuid = arg_cha_uuid
		self.characteristic = arg_cha
		self.time = arg_time
	

class Writer(GenericWriter):
	"""
	Subclass of the GenericWriter class which subscribes to a characteristic and writes them in the corresponding csv file.
	The csv file has the format: 'Unix timestamp', 'Data'
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)

		self.csv_file = open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='')
		self.csv_writer = csv.writer(self.csv_file)
		self.csv_writer.writerow(['Timestamp', 'Value', 'Comments'])
		"""
		OTHER PARAMETERS

		param csv_file:		The .csv file which will be generated and opened in append mode.
		param csv_writer:	The writer corresponding to the csv file
		"""
		# self.subscribe_and_write_Writer()			# Previously, the characteristic will be subscribed as soon its writer has been instantiated


	def __del__(self):
		if self.csv_file is None:
			return
		self.csv_file.close()

	def on_subscribe_notification_Writer(self, characteristic, event_args):
		"""
		Callback function if the nRF Dongle receives a notification
		"""
		temp_time = time.time()

		# For debugging purposes
		# value = struct.unpack("<5I", characteristic.value)
		# print("{}; {}; {}; {}".format(self.name, self.characteristic_uuid, temp_time, value))

		self.csv_writer.writerow([temp_time, characteristic.value])

	# def subscribe_and_write_Writer(self):
	# 	"""
	# 	Subscribes the characteristic.
	# 	"""
	# 	self.characteristic.subscribe(self.on_subscribe_notification_Writer).wait()
	# 	print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))


	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' in device '{}' is not writable".format(self.characteristic_uuid, self.name))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))


	def subscribe_to_characteristic(self):
		"""
		Subscribes the characteristic
		"""
		self.characteristic.subscribe(self.on_subscribe_notification_Writer).wait()
		print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))


	def unsubscribe_to_characteristic(self):
		"""
		Unsubscribes the characteristic and closes the csv file.
		"""
		print("Device: {}: Unsubscribed to characteristic: {}".format(self.name, self.characteristic_uuid))
		self.characteristic.unsubscribe().wait()
		self.csv_file.close()

	def writer_comment(self, arg_comment):
		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['', '', arg_comment])


class PerfWriter(GenericWriter):
	"""
	Subclass of the GenericWriter class which subscribes to a characteristic and writes them in the corresponding csv file.
	More precise than the Writer class using time.perf_counter(). time.perf_counter() will
	The PerfWriter uses an offset given by the Collector & DataCollector classes and the timestamp will start at 0.
	The csv file has the format: 'Timestamp', 'Data'	
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time, arg_offset):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)

		self.offset = arg_offset
		self.csv_file = open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='')
		self.csv_writer = csv.writer(self.csv_file)	
		self.csv_writer.writerow(['Timestamp', 'Value', 'Comments'])
		

		"""
		OTHER PARAMETERS
		
		param csv_file:		The .csv file which will be generated and opened in append mode.
		param csv_writer:	The writer corresponding to the csv file
		"""

		# self.subscribe_and_write_PerfWriter()

	def __del__(self):
		if self.csv_file is None:
			return
		self.csv_file.close()

	
	def on_subscribe_notification_PerfWriter(self, characteristic, event_args):
		"""
		Callback function if the nRF Dongle receives a notification
		"""
		temp_time = time.perf_counter()

		# value = struct.unpack("<10h", characteristic.value)
		# self.csv_writer.writerow([temp_time - self.offset, value])

		# For measuring and debugging purposes with CounterService
		# value = struct.unpack("<5I", characteristic.value)
		# self.csv_writer.writerow([temp_time - self.offset, value])
		# print("{}; {}; {}; {}".format(self.name, self.characteristic_uuid, temp_time - self.offset, value))

		self.csv_writer.writerow([temp_time - self.offset, characteristic.value])

	# def subscribe_and_write_PerfWriter(self):
	# 	"""
	# 	Subscribes the characteristic
	# 	"""
	# 	self.characteristic.subscribe(self.on_subscribe_notification_PerfWriter).wait()
	# 	print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))


	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' in device '{}' is not writable".format(self.characteristic_uuid, self.name))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))


	def subscribe_to_characteristic(self):
		"""
		Subscribes the characteristic
		"""
		self.characteristic.subscribe(self.on_subscribe_notification_PerfWriter).wait()
		print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))	

	def unsubscribe_to_characteristic(self):
		"""
		Unsubscribes the characteristic and closes the csv file.
		"""
		self.characteristic.unsubscribe().wait()
		self.csv_file.close()

	def writer_comment(self, arg_comment):
		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['', '', arg_comment])


class PrinterWriter(GenericWriter):
	"""
	"Writer" which prints the received notification data in the python terminal.
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)
		
		self.counter = 0
		"""
		OTHER PARAMETERS

		param counter:	A counter which increments whenever a notification has been received
		type counter:	int
		"""

		# self.subscribe_and_print_Printer()

	def on_subscribe_notification_PrinterWriter(self, characteristic, event_args):
		"""
		Callback function if the nRF Dongle receives a notification
		"""
		self.counter += 1
		temp_time = time.time()

		# For debugging purposes
		# value = struct.unpack("<5I", characteristic.value)
		# print("{}; {}; {}; {}; {}".format(self.name, self.characteristic_uuid, self.counter, temp_time, value))

		print("{}; {}; {}; {}; {}".format(self.name, self.characteristic_uuid, self.counter, temp_time, characteristic.value))

	# def subscribe_and_print_Printer(self):
	# 	"""
	# 	Subscribes the characteristic
	# 	"""
	# 	print("Subscribed to characteristic: {}".format(self.characteristic_uuid))
	# 	self.characteristic.subscribe(self.on_subscribe_notification_PrinterWriter).wait()

	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' in device '{}' is not writable".format(self.characteristic_uuid, self.name))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))

	def subscribe_to_characteristic(self):
		"""
		Subscribes the characteristic
		"""
		self.characteristic.subscribe(self.on_subscribe_notification_PrinterWriter).wait()
		print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))	

	def unsubscribe_to_characteristic(self):
		"""
		Unsubscribes the characteristic
		"""
		self.characteristic.unsubscribe().wait()


class ReadRequestWriter(GenericWriter):
	"""
	Writer class which periodically does read requests to the characteristic.
	NOTE: Will not work and will raise exception if the characteristic is not readable!
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)

		self.csv_file = open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='')
		self.csv_writer = csv.writer(self.csv_file)
		self.csv_writer.writerow(['Timestamp', 'Value', 'Comments'])
		self.request_status = False
		# self.delay = 0.3
		"""
		OTHER PARAMETERS

		param csv_file:			The .csv file which will be generated and opened in append mode.
		param csv_writer:		The writer corresponding to the csv file

		param request_status:	An attribute for checking whether the nRF dongle should continue with read requests or not. True if it should continue read requests.
		type request_status:	bool

		param delay:			An attribute for delaying the time between two consecutive read request
		type delay:				float
		"""
		
		# self.start_time = time.perf_counter()
		# self.initiate_read_request()


	def __del__(self):
		if self.csv_file is None:
			return
		self.csv_file.close()

	def on_read_request(self, characteristic, event_args):
		"""
		Callback function whenever a read request succeeds.
		"""
		temp_time = time.time()
		# value = struct.unpack("<5I", characteristic.value)
		# print("{}; {}; {}; {}; {}".format(self.name, self.characteristic_uuid, self.counter, temp_time, value))
		self.csv_writer.writerow([temp_time, characteristic.value])

		# self.end_time = time.perf_counter()
		
		# Ask for the next read request
		if self.request_status is True:
			# time.sleep(self.delay)
			self.characteristic.read().then(self.on_read_request)

	# def initiate_read_request(self):
	# 	"""
	# 	Starts the periodic read request
	# 	"""
	# 	self.request_status = True
	# 	self.characteristic.read().then(self.on_read_request)
	# 	print("Initiating read requests on characteristic: {}".format(self.characteristic_uuid))

	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' in device '{}' is not writable".format(self.characteristic_uuid, self.name))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))


	def subscribe_to_characteristic(self):
		"""
		"Subscribes" the characteristic
		"""
		self.request_status = True
		self.characteristic.read().then(self.on_read_request)
		print("Device: {}: Initiating read requests to characteristic: {}".format(self.name, self.characteristic_uuid))
	
	def unsubscribe_to_characteristic(self):
		"""
		Stops the periodic read request
		"""
		self.request_status = False
		# Sleep for a short duration so that the remaining on going on_read_request can still write the values within the csv file.
		time.sleep(3)
		self.csv_file.close()
		# print("Requested in total: {} read requests to characteristic '{}' within {}".format(self.counter, self.characteristic_uuid, self.end_time - self.start_time))

	def writer_comment(self, arg_comment):
		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['', '', arg_comment])



"""
Writers used for debugging purposes
"""

class CounterWriter(GenericWriter):
	"""
	Writer which only counts the amount of received notification. Has the fastest on_notification callback.
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)	

		self.counter = 0
		"""
		OTHER PARAMETERS

		param counter:	A counter which increments whenever a notification has been received
		type counter:	int
		"""
		
		# Time when the CounterWriter has been instantiated. For testing purposes
		# self.start_time = time.perf_counter()

		# self.subscribe_and_count_CounterWriter()

	# @timer.csv_timer
	def on_subscribe_notification_CounterWriter(self, characteristic, event_args):
		self.counter += 1

	# @timer.csv_timer
	# def subscribe_and_count_CounterWriter(self):
	# 	print("Subscribed to characteristic: {}".format(self.characteristic_uuid))
	# 	self.characteristic.subscribe(self.on_subscribe_notification_CounterWriter).wait()


	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' is not writable".format(self.characteristic_uuid))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))


	def subscribe_to_characteristic(self):
		"""
		Subscribes the characteristic
		"""
		self.start_time = time.perf_counter()
		self.characteristic.subscribe(self.on_subscribe_notification_CounterWriter).wait()
		print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))

	def unsubscribe_to_characteristic(self):
		self.characteristic.unsubscribe().wait()
		print("Received in total: {} notifications from characteristic '{}' within {} seconds".format(self.counter, self.characteristic_uuid, time.perf_counter() - self.start_time))


class DummyWriter(GenericWriter):
	"""
	Dummy Writer which causes an extra delay during a notification event. Used for debugging and testing
	"""
	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)
		self.counter = 0
		self.delay = 0.5
		# self.subscribe_to_characteristic_DummyWriter()

	# @timer.csv_timer
	def on_subscribe_notification_DummyWriter(self, characteristic, event_args):
		"""
		Callback function if the nRF Dongle receives a notification
		"""
		temp_time = time.time()
		print("Received Notification at time {}".format(temp_time))
		print("Waiting for {} seconds".format(self.delay))
		time.sleep(self.delay)
		print("Done waiting")
		print("Writing csv...")
		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow([temp_time, str(characteristic.value)])
			self.counter += 1
		print("Done writing csv... Counter: {}".format(self.counter))
			
	# @timer.csv_timer
	# def subscribe_to_characteristic_DummyWriter(self):
	# 	"""
	# 	Subscribes the characteristic
	# 	"""
	# 	self.characteristic.subscribe(self.on_subscribe_notification_DummyWriter).wait()
	# 	print("Subscribed to characteristic: {}".format(self.characteristic_uuid))


	def write_characteristic(self, value):
		"""
		Writes a value to the characteristic

		param value:	The value to be written
		type:			str or int
		"""
		if self.characteristic.writable is False:
			print("Characteristic '{}' in device '{}' is not writable".format(self.characteristic_uuid, self.name))
			return
		else:
			self.characteristic.write(value)
			print("Wrote '{}' to characteristic '{}' to device '{}'".format(value, self.characteristic_uuid, self.name))


	def subscribe_to_characteristic(self):
		"""
		Subscribes the characteristic
		"""
		self.characteristic.subscribe(self.on_subscribe_notification_DummyWriter).wait()
		print("Device: {}: Subscribed to characteristic: {}".format(self.name, self.characteristic_uuid))

	# @timer.csv_timer
	def unsubscribe_to_characteristic(self):
		"""
		Unsubscribes the characteristic
		"""
		self.characteristic.unsubscribe().wait()
		print("Received in total: {} notifications from characteristic '{}' with delay: {} seconds".format(self.counter, self.characteristic_uuid, self.delay))

	def writer_comment(self, arg_comment):
		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
			csv_writer = csv.writer(csv_file)
			csv_writer.writerow(['', '', arg_comment])









### OLD CODE ###################

# class Writer2(GenericWriter):
# 	"""
# 	OLD: Writer2 which is essentially the same as Writer, the difference is the order of code sequence.
# 	In this case it first opens ALL csv_files and then subscribes. Rather than open and subscribe for each characteristic
# 	Note: No difference to Writer since opening a csv time does not take too much time.
# 	"""
# 	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
# 		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)
# 		self.csv_file = open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='')
# 		self.csv_writer = csv.writer(self.csv_file)

# 	def __del__(self):
# 		print("Closing File..")
# 		self.csv_file.close()
	
# 	# @timer.csv_timer
# 	def on_subscribe_notification_Writer2(self, characteristic, event_args):
# 		temp_time = time.time()

# 		### TEMPORARY FOR DEBUGGING PURPOSES ########################################
# 		# value = struct.unpack("<5I", characteristic.value)							# Used with CounterService from Silvano Cortesi
# 		# self.csv_writer.writerow([temp_time, value])
# 		#############################################################################

# 		self.csv_writer.writerow([temp_time, str(characteristic.value)])
# 		self.counter += 1

# 	# @timer.csv_timer
# 	def subscribe_to_characteristic_Writer2(self):
# 		print("Subscribed to characteristic: {}".format(self.characteristic_uuid))
# 		self.characteristic.subscribe(self.on_subscribe_notification_Writer2).wait()

# 	def unsubscribe_to_characteristic(self):
# 		self.characteristic.unsubscribe().wait()
# 		self.csv_file.close()
# 		print("Received in total: '{}' notifications from characteristic: '{}'".format(self.counter, self.characteristic_uuid))


# class InefficientWriter(GenericWriter):
# 	"""
# 	OLD: First Writer, which was more inefficient than Writer and Writer2. Needs to reopen csv file as soon as it handles notification.
# 	"""
# 	def __init__(self, arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time):
# 		super().__init__(arg_name, arg_service, arg_cha_uuid, arg_cha, arg_time)
# 		self.subscribe_to_characteristic_InefficientWriter()

# 	# @timer.csv_timer
# 	def on_subscribe_notification_InefficientWriter(self, characteristic, event_args):
# 		temp_time = time.time()
# 		with open(os.path.join('data', str(self.name), str(self.service), str(self.characteristic_uuid), '{}.csv'.format(self.time)), 'a', newline='') as csv_file:
# 			csv_writer = csv.writer(csv_file)
# 			csv_writer.writerow([temp_time, str(characteristic.value)])
# 			self.counter += 1
	
# 	# @timer.csv_timer
# 	def subscribe_to_characteristic_InefficientWriter(self):
# 		self.characteristic.subscribe(self.on_subscribe_notification_InefficientWriter).wait()
# 		print("Subscribed to characteristic: {}".format(self.characteristic_uuid))

# 	# @timer.csv_timer
# 	def unsubscribe_to_characteristic(self):
# 		self.characteristic.unsubscribe().wait()
# 		print("Received in total: {} notifications from characteristic '{}'".format(self.counter, self.characteristic_uuid))






