"""
file name:			timer.py
author:				Jackie Lim
created:			30. March 2021

brief:				This file contains wrappers which are used for measuring function durations.
"""

"""
Import statement
"""

import time
import functools
import os
import csv

def timer(func):
	"""
	Wrapper to determine how long a function takes to process. Prints out the time in python terminal. See https://realpython.com/primer-on-python-decorators/#timing-functions
	"""
	@functools.wraps(func)
	def wrapper_timer(*args, **kwargs):
		start_time = time.perf_counter()
		value = func(*args, **kwargs)
		end_time = time.perf_counter()
		run_time = end_time - start_time
		print("Finished '{}' in '{}' seconds".format(func.__name__, run_time))
		return value

	return wrapper_timer

def csv_timer(func):
	"""
	Wrapper to determine how long a function takes to process. Saves the time in the csv file located in /measurement/'function_name'
	"""
	@functools.wraps(func)
	def wrapper_timer(*args, **kwargs):
		start_time = time.perf_counter()
		value = func(*args, **kwargs)
		end_time = time.perf_counter()
		run_time = end_time - start_time
		with open(os.path.join('measurement', '{}.csv'.format(func.__name__)), 'a', newline='') as measure_file:
			writer = csv.writer(measure_file)
			writer.writerow([run_time])
		return value
		
	return wrapper_timer


def main():
	counter = 0

	@csv_timer
	def temp_func(arg_counter):
		arg_counter += 1

	temp_func(counter)

if __name__ == "__main__":
	main()