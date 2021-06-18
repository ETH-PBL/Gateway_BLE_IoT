"""
file name:			constants.py
author:				Jackie Lim
created:			30. March 2021

brief:				This file contains constants which are used within the whole framework
"""


"""
Configuration of nRF device
"""
DEFAULT_COM_PORT = 'COM6'
DEFAULT_NUMBER_CUSTOM_UUID = 20
DEFAULT_NUMBER_PERIPHERALS = 2
DEFAULT_HW_QUEUE_NOTIFICATION = 16
DEFAULT_HW_QUEUE_WRITE_COMMANDS = 16
DEFAULT_ATTRIBUTE_TABLE_SIZE = 4096


"""
Configuration connection parameters
"""
DEFAULT_MIN_CONN_INT_MS = 7.5 
DEFAULT_MAX_CONN_INT_MS = 30
DEFAULT_TIMEOUT_MS = 4000
DEFAULT_SLAVE_LATENCY = 0
