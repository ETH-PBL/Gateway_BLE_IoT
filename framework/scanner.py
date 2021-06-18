"""
file name:			scanner.py
author:				Jackie Lim
created:			6. April 2021

brief:				This file contains classes which are responsible for scanning other devices with the nRF52480 Dongle.
"""

"""
Import statement
"""
import timer
import customexception

from connection import ConnectionManager, Connection

class Scanner(object):
	"""
	Main Class which is responsible for handling the nRF Device to scan other devices. 
	"""

	def __init__(self, arg_ble_device):
		"""
		INPUT PARAMETERS 

		param 	arg_ble_device: 	The nRF device
		type	arg_ble_device: 	blatann.BleDevice
		"""
		self.ble_device = arg_ble_device

		self.scan_report_collection = None
		self.scan_report_dict = None
		"""
		OTHER PARAMETERS 

		param scan_report_collection:	The scan report of the nRF device
		type scan_report_collection: 	blatann.gap.advertise_data.ScanReportCollection

		param scan_report_dict:			A simplified version of the scan report. Contains Name and Address of peripherals
		type scan_report_dict: 			dict
										Format: {'Name': 'Address'}
		"""

	def __str__(self):
		return("Scannner class of the nRF Device at port: '{}'".format(self.ble_device)) 

	def reset(self):
		"""
		For re-scanning purposes
		"""
		print("Clear report_collection...")
		self.scan_report_collection.clear()	
		self.scan_report_collection = None	
		self.scan_report_dict = None

	def _scan_report_converter(self, arg_scan_report):
		"""
		PRIVATE FUNCTION. Required to convert scan_report_collection into another simplified scan_report_dict.

		param	arg_scan_report: 	A collection of scanned devices
		type	arg_scan_report: 	blatann.gap.advertise_data.ScanReportCollection
		"""
		return_val = {report.device_name:report.peer_address for report in arg_scan_report.advertising_peers_found}
		
		if not return_val:
			print("No devices have been found.")
			return
		else:
			self.scan_report_dict = return_val

	def scan_for_devices(self):
		"""
		SYNCHRONOUS PROCESS
		Scans for nearby devices and saves them in the attribute self.scan_report_dict. 
		Note: Do not clear cache with .clear else you will lose advertising payload, which includes peer.name after connecting to it.
		"""
		if self.scan_report_collection is not None:
			self.reset()

		print("Scanning for devices...")
		self.ble_device.scanner.set_default_scan_params(timeout_seconds = 4)			 
		self.scan_report_collection = self.ble_device.scanner.start_scan().wait()		
		self._scan_report_converter(self.scan_report_collection)
		print("Finished scanning devices")

	def show_scanned_devices(self):
		"""
		Shows all scanned devices
		"""
		print(self.scan_report_dict)

	def createConnectionManager(self):
		"""
		Returns an object of the ConnectionManager with the corresponding nRF device and the scan report.
		exception: If no devices has been scanned yet, raises an InvalidStateException
		"""
		if self.scan_report_dict is None:
			raise customexception.InvalidStateException("Cannot create ConnectionManager if scan report is empty")
		else:
			return ConnectionManager(self.ble_device, self.scan_report_dict)