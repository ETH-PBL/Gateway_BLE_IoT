"""
file name:			run.py
author:				Jackie Lim
created:			7. May 2021

brief:				This file contains the script for plotting the packet reception for the framework. Used for the report. Not recommended to use
					it for actual data plotting.
"""
"""
Import statement
"""
import csv
import os
import struct
import numpy as np
import matplotlib.pyplot as plot
import pandas
from datetime import datetime
import time

from matplotlib.ticker import AutoMinorLocator

"""
Definitions
"""
global PSNODE, PSSERVICE, PSCHAR1, PSCHAR2, COUNTERDEVICE, COUNTERDEVICE1, COUNTERDEVICE2, COUNTERDEVICE3, COUNTERDEVICE4, COUNTERSERVICE, OLD_COUNTERSERVICE, COUNTERCHAR1, OLD_COUNTERCHAR1, COUNTERCHAR2, start_time, unixtime

PSNODE = "P&SNode"
PSSERVICE = "00000000-0001-11e1-9ab4-0002a5d5c51b"
PSCHAR1 = "001d0000-0001-11e1-ac36-0002a5d5c51b"
PSCHAR2 = "00020000-0001-11e1-ac36-0002a5d5c51b"

COUNTERDEVICE = "CounterTester"
COUNTERDEVICE1 = "CounterTester1"
COUNTERDEVICE2 = "CounterTester2"
COUNTERDEVICE3 = "CounterTester3"
COUNTERDEVICE4 = "CounterTester4"
 
COUNTERSERVICE = "ad4a4001-5562-4112-9aa8-0aa23d0ce57a"
OLD_COUNTERSERVICE = "020013ac-4202-bcbc-eb11-43a172103323"
COUNTERCHAR1 = "ad4a4041-5562-4112-9aa8-0aa23d0ce57a"
OLD_COUNTERCHAR1 = "020013ac-4202-bcbc-eb11-43a172103324"
COUNTERCHAR2 = "020013ac-4202-bcbc-eb11-43a172103325"


""" 
Notable measurements 
"""

""" 
Measurement of P&SNode
GROUP1
"""
""" Old driver """
global psnode38, psnode38_2

psnode38 = "130421_144308"      # unix_convert, header = None
psnode38_2 = "140421_161257"   # unix_convert, header = None

""" New driver """
global psnode37, psnode37_2

psnode37 = "060521_074944"      # unix_convert, header = None

psnode37_2 = "150521_101750"    # No unix_convert, header = 'infer'



""" 
Measurement of a single peer connection with CounterDevice
"""
""" Old driver (py38) 
	GROUP2
""" 
global counter38_50, counter38_100

counter38_50 = "290421_080946"
counter38_100 = "290421_081119"



""" 
New driver (py37), default connection parameter of (15,30,4000,0) 
Note: All done with standard Writer. Points do overlap due to Writer being not precise enough
GROUP3
"""
global counter37_50, counter37_100, counter37_500

counter37_50 = "070521_091503"
counter37_100 = "070521_133441"
counter37_500 = "080521_111810"



"""
New driver (py37), different connection parameter (7.5,x,4000,0) where x varies.
Note: Done with PerfWriter.
GROUP4
"""
counter37_100_30 = "180521_111429"

counter37_1000_7_5 = "150521_104646"
counter37_1000_10 = "150521_104351"
counter37_1000_20 = "150521_104119"

counter37_1000_12_5 = "110521_134101"	# Header: None!
counter37_1000_8_75 = "190521_092846"



"""
Measurement of 4 peer CounterDevices with new driver (py37). Standard connection parameter (15,30,4000,0). 
Note: Done with Writer
GROUP5
"""
global four_device_2Hz, four_device_10Hz, four_device_12_5Hz, four_device_20Hz, four_device_25Hz, four_device_40Hz, four_device_50Hz, four_device_83_3Hz, four_device_100Hz, four_device_125Hz, four_device_166_6Hz, four_device_200Hz

four37_2 = "070521_113712"
four37_10 = "070521_115852"
four37_12_5 = "070521_124542"
four37_20 = "070521_125321"
four37_25 = "070521_130252"
four37_40 = "070521_130753"
four37_50 = "070521_131443"
four37_83_3 = "070521_132225"
four37_100 = "070521_132848"
four37_125 = "070521_135229"
four37_166_6 = "070521_135658"

four37_200 = "120521_124501"

"""
Measurement of 4 peer CounterDevices with new driver (py37), different connection parameters (7.5,x,4000,0) where x varies
GROUP6
"""
four37_200_7_5 = "120521_115342"
four37_200_12_5 = "120521_105706"
four37_200_15 = "120521_115557"
four37_200_30 = "120521_124333"
four37_200_60 = "120521_124730"

four37_200_25 = "170521_113142"

five37_100 = "170521_164918"
five37_200 = "170521_164052"

"""
Functions:
"""

"""
Function which offsets the timestamp values to the beginning of the measurement (Only necessary if not measured with PerfWriter)
param str_datetime: The name of the csv file
type str_datetime: str

returns: The time converted in unixtime (in float)
"""
def convert_unixtime(str_datetime):
	datetime_obj = datetime.strptime(str_datetime, "%d%m%y_%H%M%S")
	unixtime = time.mktime(datetime_obj.timetuple())
	return unixtime

"""
Returns a numpy array with timestamps as elements, which can be further processed to be plotted
param arg_file: The csv file containing the datas
type arg_file: The location of the csv file.

returns: numpy array with timestamp from csv file as elements
"""
def data_to_numpy(arg_file, arg_filename, arg_header, unix_offset):

	def convert_unixtime_func(value):
		return value - offset

	raw_dataframe = pandas.read_csv(arg_file, header = arg_header, usecols=[n for n in range(2)])
	raw_dataframe_timestamp = raw_dataframe.iloc[:,0]

	if unix_offset == True:
		offset = convert_unixtime(arg_filename)
		dataframe_timestamp = raw_dataframe_timestamp.apply(convert_unixtime_func)
	else:
		dataframe_timestamp = raw_dataframe_timestamp

	numpy_timestamp = dataframe_timestamp.to_numpy()

	return numpy_timestamp


"""
Plots the data from the measurements from the data directory
WARNING: Do not use this unless you know which Writer were used during the measurement. 
The following functions were used for plotting data for the report. They do not plot the data itself but the timestamp when they did arrive.
"""

"""
For measurement with P&SNode GROUP1
"""
def get_ps_data(filename):
	csv_file1 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR1, "{}.csv".format(filename))
	csv_file2 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR2, "{}.csv".format(filename))
	nump_arr1 = data_to_numpy(csv_file1, filename, 'infer', True)
	nump_arr2 = data_to_numpy(csv_file2, filename, 'infer', True)

	fig, ax = plot.subplots()

	plot.title("{}".format(filename))
	plot.xlabel("Time in seconds")

	plot.grid(axis='x', which='major', linestyle='-')
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.minorticks_on()

	plot.yticks([0,1,2,3], ['Overlap', 'Data reception 1', '2',''])

	plot.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, 'r.', label=PSCHAR2)
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, 'b.', label=PSCHAR1)

	plot.plot(nump_arr1, np.zeros_like(nump_arr1) , 'b.')
	plot.plot(nump_arr2, np.zeros_like(nump_arr2) , 'r.')

	plot.ylim(top = 2.5)
	plot.yticks([0,1,2])
	### For "zoomed in" plots ###################################
	# left_val = 8.27
	# right_val = 8.275
	# interval_val = 0.005

	# plot.xticks(np.arange(left_val,right_val,interval_val))
	# plot.xlim(left=left_val, right=right_val)
	#############################################################

	# minor_locator = AutoMinorLocator(5)
	# ax.xaxis.set_minor_locator(minor_locator)
	plot.grid(axis='x', which='major', linestyle='-')
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.legend()
	plot.show()


"""
For measurement with the old driver on python version 3.8 on the CounterService
GROUP2
"""
def get_single_cs_data_py38(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE, OLD_COUNTERSERVICE, OLD_COUNTERCHAR1, "{}.csv".format(filename))
	nump_arr1 = data_to_numpy(csv_file1, filename, None, True)

	fig, ax = plot.subplots()

	plot.title("{}".format(filename))
	plot.xlabel("Time in seconds")

	plot.grid(axis='x', which='major', linestyle='-')
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.4)
	plot.minorticks_on()

	### For "zoomed in" plots ###################################
	# left_val = 3
	# right_val = 3.6
	# interval_val = 0.15

	# plot.xticks(np.arange(left_val,right_val,interval_val))
	# plot.xlim(left=left_val, right=right_val)
	#############################################################


	minor_locator = AutoMinorLocator(5)
	ax.xaxis.set_minor_locator(minor_locator)

	plot.yticks([1],['1'])
	# plot.xticks(np.arange(0, nump_arr1.max(),1))

	val = 1
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + val, 'b.', label = OLD_COUNTERCHAR1)
	plot.legend()

	# plot.xlim(left=min(nump_arr1.min()-0.5, 0))
	plot.show()


"""
For measurements with the new driver on python 3.7 with a single CounterDevice.
GROUP3
"""
def get_single_cs_data_py37(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	nump_arr1 = data_to_numpy(csv_file1, filename, 'infer', False)

	# print(nump_arr1.size)

	fig, ax = plot.subplots()

	plot.title("{}".format(filename))
	plot.xlabel("Time in seconds")
	plot.grid(axis='x', which='major', linestyle='-')

	plot.minorticks_on()
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.yticks([0,1])
	plot.xticks(np.arange(0,nump_arr1.max(),1))

	minor_locator = AutoMinorLocator(4)
	ax.xaxis.set_minor_locator(minor_locator)


	# ## For "zoomed in" plots ###################################
	left_val = 6
	right_val = 6.09
	interval_val = 0.03

	plot.xticks(np.arange(left_val,right_val,interval_val))
	plot.xlim(left=left_val, right=right_val)
	# ############################################################

	val = 1
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + val, 'b.', label=COUNTERCHAR1)
	plot.legend()

	plot.show()


"""
For measurements with the new driver on python 3.7 with a single CounterDevice. Testing the influence of different ConnectionParameters
GROUP4
"""
def get_single_cs_data_py37_con_interval():
	csv_file1 = os.path.join('data', COUNTERDEVICE, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(counter37_1000_7_5))
	csv_file2 = os.path.join('data', COUNTERDEVICE, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(counter37_1000_10))
	csv_file3 = os.path.join('data', COUNTERDEVICE, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(counter37_1000_20))

	nump_arr1 = data_to_numpy(csv_file1, counter37_1000_7_5, 'infer', False)
	nump_arr2 = data_to_numpy(csv_file2, counter37_1000_10, 'infer', False)
	nump_arr3 = data_to_numpy(csv_file3, counter37_1000_20, 'infer', False)

	fig, ax = plot.subplots()


	plot.title("connection interval, 1000Hz")
	plot.xlabel("Time in seconds")
	plot.grid(axis='x', which='major', linestyle='-')

	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)
	plot.minorticks_on()

	# ## For "zoomed in" plots ###################################
	left_val = 6.5
	right_val = 6.6
	interval_val = 0.05

	plot.xticks(np.arange(left_val,right_val,interval_val))
	plot.xlim(left=left_val, right=right_val)
	# ############################################################

	minor_locator = AutoMinorLocator(5)
	ax.xaxis.set_minor_locator(minor_locator)

	plot.ylim(top=3.5)
	plot.yticks([1,2,3])

	plot.plot(nump_arr3, np.zeros_like(nump_arr3) + 3, '.', label= '20ms, {}'.format(counter37_1000_20))
	plot.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, '.', label= '10ms, {}'.format(counter37_1000_10))
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, '.', label= '7.5ms, {}'.format(counter37_1000_7_5))


	plot.legend()

	
	# plot.xlim(left=min(nump_arr1.min(),nump_arr2.min(),nump_arr3.min()))
	plot.show()


"""
For measurements with the new driver on python 3.7 with 4 different devices.
GROUP5
"""
def get_4_cs_data_py37(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE1, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file2 = os.path.join('data', COUNTERDEVICE2, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file3 = os.path.join('data', COUNTERDEVICE3, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file4 = os.path.join('data', COUNTERDEVICE4, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))

	nump_arr1 = data_to_numpy(csv_file1, filename, None, True)
	nump_arr2 = data_to_numpy(csv_file2, filename, None, True)
	nump_arr3 = data_to_numpy(csv_file3, filename, None, True)
	nump_arr4 = data_to_numpy(csv_file4, filename, None, True)

	plot.title("{} notification".format(COUNTERDEVICE))
	plot.xlabel("Time since subscription")
	plot.grid(axis='x', which='major', linestyle='-')

	plot.xlabel("Time in seconds")

	plot.minorticks_on()
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.yticks([0,1,2,3,4])
	# plot.xticks(np.arange(0,nump_arr1.max(),1))

	val = 1
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, '.')
	plot.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, '.')
	plot.plot(nump_arr3, np.zeros_like(nump_arr3) + 3, '.')
	plot.plot(nump_arr4, np.zeros_like(nump_arr4) + 4, '.')

	plot.plot(nump_arr1, np.zeros_like(nump_arr1), '.')
	plot.plot(nump_arr2, np.zeros_like(nump_arr2), '.')
	plot.plot(nump_arr3, np.zeros_like(nump_arr3), '.')
	plot.plot(nump_arr4, np.zeros_like(nump_arr4), '.')



	plot.xlim(left=nump_arr1.min())
	plot.show()
	

"""
For measurements with the new driver on python 3.7. Testing the influence of different connection Parameters
"""
def get_4_cs_data_py37_con_interval(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE1, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file2 = os.path.join('data', COUNTERDEVICE2, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file3 = os.path.join('data', COUNTERDEVICE3, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file4 = os.path.join('data', COUNTERDEVICE4, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))

	# csv_file5 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR1, "{}.csv".format(filename))
	# csv_file6 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR2, "{}.csv".format(filename))

	nump_arr1 = data_to_numpy(csv_file1, filename, 'infer', False)
	nump_arr2 = data_to_numpy(csv_file2, filename, 'infer', False)
	nump_arr3 = data_to_numpy(csv_file3, filename, 'infer', False)
	nump_arr4 = data_to_numpy(csv_file4, filename, 'infer', False)
	# nump_arr5 = data_to_numpy(csv_file5, filename, 'infer', False)
	# nump_arr6 = data_to_numpy(csv_file6, filename, 'infer', False)

	fig, ax = plot.subplots()


	plot.title("{}".format(filename))
	plot.xlabel("Time in seconds")
	plot.grid(axis='x', which='major', linestyle='-')

	plot.minorticks_on()
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.yticks([0,1,2,3,4],['Overlap','1','2','3','4'])
	# plot.xticks(np.arange(0,max(nump_arr1.max(),nump_arr2.max(),nump_arr3.max(),nump_arr4.max()),1))

	# plot.plot(nump_arr6, np.zeros_like(nump_arr6) + 6, 'cx',label=PSCHAR2)
	# plot.plot(nump_arr5, np.zeros_like(nump_arr5) + 5, 'mx',label=PSCHAR1)
	plot.plot(nump_arr4, np.zeros_like(nump_arr4) + 4, 'b.',label="Device: {}".format(COUNTERDEVICE4))
	plot.plot(nump_arr3, np.zeros_like(nump_arr3) + 3, 'r.',label="Device: {}".format(COUNTERDEVICE3))
	plot.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, 'g.',label="Device: {}".format(COUNTERDEVICE2))
	plot.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, 'y.',label="Device: {}".format(COUNTERDEVICE1))

	minor_locator = AutoMinorLocator(4)
	ax.xaxis.set_minor_locator(minor_locator)

	plot.xlabel("Time in seconds")

	plot.plot(nump_arr1, np.zeros_like(nump_arr1), 'y.')
	plot.plot(nump_arr2, np.zeros_like(nump_arr2), 'g.')
	plot.plot(nump_arr3, np.zeros_like(nump_arr3), 'r.')
	plot.plot(nump_arr4, np.zeros_like(nump_arr4), 'b.')
	# plot.plot(nump_arr5, np.zeros_like(nump_arr5), 'mx')
	# plot.plot(nump_arr6, np.zeros_like(nump_arr6), 'cx')

	plot.ylim(top=6)

	plot.legend()
	
	# plot.xlim(right=7)

	## For "zoomed in" plots ###################################
	# left_val = 11
	# right_val = 11.06
	# interval_val = 0.03

	# plot.xticks(np.arange(left_val,right_val,interval_val))
	# plot.xlim(left=left_val, right=right_val)
	############################################################


	plot.show()

def plot_perfwriter(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE1, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file2 = os.path.join('data', COUNTERDEVICE2, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file3 = os.path.join('data', COUNTERDEVICE3, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file4 = os.path.join('data', COUNTERDEVICE4, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))

	csv_file5 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR1, "{}.csv".format(filename))
	csv_file6 = os.path.join('data', PSNODE, PSSERVICE, PSCHAR2, "{}.csv".format(filename))

	nump_arr1 = data_to_numpy(csv_file1, filename, 'infer', False)
	nump_arr2 = data_to_numpy(csv_file2, filename, 'infer', False)
	nump_arr3 = data_to_numpy(csv_file3, filename, 'infer', False)
	nump_arr4 = data_to_numpy(csv_file4, filename, 'infer', False)
	nump_arr5 = data_to_numpy(csv_file5, filename, 'infer', False)
	nump_arr6 = data_to_numpy(csv_file6, filename, 'infer', False)

	fig, ax = plot.subplots()
	plot.title("{}, 100Hz".format(filename))

	ax.plot(nump_arr6, np.zeros_like(nump_arr6) + 6, 'cx',label="Device: {}, {}".format(PSNODE,PSCHAR2))
	ax.plot(nump_arr5, np.zeros_like(nump_arr5) + 5, 'mx',label="Device: {}, {}".format(PSNODE,PSCHAR1))
	ax.plot(nump_arr4, np.zeros_like(nump_arr4) + 4, 'b.',label="Device: {}".format(COUNTERDEVICE4))
	ax.plot(nump_arr3, np.zeros_like(nump_arr3) + 3, 'r.',label="Device: {}".format(COUNTERDEVICE3))
	ax.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, 'g.',label="Device: {}".format(COUNTERDEVICE2))
	ax.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, 'y.',label="Device: {}".format(COUNTERDEVICE1))


	ax.plot(nump_arr1, np.zeros_like(nump_arr1), 'y.')
	ax.plot(nump_arr2, np.zeros_like(nump_arr2), 'g.')
	ax.plot(nump_arr3, np.zeros_like(nump_arr3), 'r.')
	ax.plot(nump_arr4, np.zeros_like(nump_arr4), 'b.')
	ax.plot(nump_arr5, np.zeros_like(nump_arr5), 'mx')
	ax.plot(nump_arr6, np.zeros_like(nump_arr6), 'cx')	
	
	plot.yticks([0,1,2,3,4,5,6],['Overlap','1','2','3','4', '5', '6'])

	minor_locator = AutoMinorLocator(5)
	ax.xaxis.set_minor_locator(minor_locator)
	plot.grid(axis='x', which='major', linestyle='-')
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.ylim(top=12)
	plot.xlim(right=7,left=0)
	
	plot.xlabel("Time in seconds")

	## For "zoomed in" plots ###################################
	left_val = 3
	right_val = 3.1
	interval_val = 0.0375

	plot.xticks(np.arange(left_val,right_val,interval_val))
	plot.xlim(left=left_val, right=right_val)
	############################################################

	plot.legend()
	plot.show()

def plot_eight_device(filename):
	csv_file1 = os.path.join('data', COUNTERDEVICE1, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file2 = os.path.join('data', COUNTERDEVICE2, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file3 = os.path.join('data', COUNTERDEVICE3, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file4 = os.path.join('data', COUNTERDEVICE4, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file5 = os.path.join('data', 'CounterTester5', COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file6 = os.path.join('data', 'CounterTester6', COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file7 = os.path.join('data', 'CounterTester7', COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	csv_file8 = os.path.join('data', 'CounterTester8', COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(filename))
	

	nump_arr1 = data_to_numpy(csv_file1, filename, 'infer', False)
	nump_arr2 = data_to_numpy(csv_file2, filename, 'infer', False)
	nump_arr3 = data_to_numpy(csv_file3, filename, 'infer', False)
	nump_arr4 = data_to_numpy(csv_file4, filename, 'infer', False)
	nump_arr5 = data_to_numpy(csv_file5, filename, 'infer', False)
	nump_arr6 = data_to_numpy(csv_file6, filename, 'infer', False)
	nump_arr7 = data_to_numpy(csv_file7, filename, 'infer', False)
	nump_arr8 = data_to_numpy(csv_file8, filename, 'infer', False)


	fig, ax = plot.subplots()
	plot.title("{}".format(filename))


	ax.plot(nump_arr8, np.zeros_like(nump_arr8) + 8,'bx',label="Device: {}".format('CounterTester8'))
	ax.plot(nump_arr7, np.zeros_like(nump_arr7) + 7,'rx',label="Device: {}".format('CounterTester7'))
	ax.plot(nump_arr6, np.zeros_like(nump_arr6) + 6, 'gx',label="Device: {}".format('CounterTester6'))
	ax.plot(nump_arr5, np.zeros_like(nump_arr5) + 5, 'yx',label="Device: {}".format('CounterTester5'))
	ax.plot(nump_arr4, np.zeros_like(nump_arr4) + 4, 'b.',label="Device: {}".format(COUNTERDEVICE4))
	ax.plot(nump_arr3, np.zeros_like(nump_arr3) + 3, 'r.',label="Device: {}".format(COUNTERDEVICE3))
	ax.plot(nump_arr2, np.zeros_like(nump_arr2) + 2, 'g.',label="Device: {}".format(COUNTERDEVICE2))
	ax.plot(nump_arr1, np.zeros_like(nump_arr1) + 1, 'y.',label="Device: {}".format(COUNTERDEVICE1))


	ax.plot(nump_arr1, np.zeros_like(nump_arr1), 'y.')
	ax.plot(nump_arr2, np.zeros_like(nump_arr2), 'g.')
	ax.plot(nump_arr3, np.zeros_like(nump_arr3), 'r.')
	ax.plot(nump_arr4, np.zeros_like(nump_arr4), 'b.')
	ax.plot(nump_arr5, np.zeros_like(nump_arr5), 'yx')
	ax.plot(nump_arr6, np.zeros_like(nump_arr6), 'gx')
	ax.plot(nump_arr7, np.zeros_like(nump_arr7), 'rx')	
	ax.plot(nump_arr8, np.zeros_like(nump_arr8), 'bx')	

	
	plot.yticks([0,1,2,3,4,5,6,7,8],['Overlap','1','2','3','4', '5', '6', '7','8'])

	minor_locator = AutoMinorLocator(8)
	ax.xaxis.set_minor_locator(minor_locator)
	plot.grid(axis='x', which='major', linestyle='-')
	plot.grid(axis='x', which='minor', linestyle='-', alpha=0.5)

	plot.ylim(top=20)
	plot.xlim(left=0)
	
	plot.xlabel("Time in seconds")

	## For "zoomed in" plots ###################################
	left_val = 3.
	right_val = 3.06 
	interval_val = 0.06

	plot.xticks(np.arange(left_val,right_val,interval_val))
	plot.xlim(left=left_val, right=right_val)
	############################################################

	plot.legend()
	plot.show()




def restore_raw_data():
	arg_file = "070521_145200"
	csv_file = os.path.join('data', COUNTERDEVICE1, COUNTERSERVICE, COUNTERCHAR1, "{}.csv".format(arg_file))
	raw_dataframe = pandas.read_csv(csv_file, header = None, usecols=[n for n in range(2)])
	raw_dataframe_timestamp = raw_dataframe.iloc[:,1]
	
	print(type(raw_dataframe_timestamp[1]))


	# value = struct.unpack("<5I",eval(raw_dataframe_timestamp[1]))

	# print(value)

	print(struct.unpack("<5I", eval("b'Q!\x00\x00\x00\x00\x00\x00c\x00\x00\x00d\x00\x00\x00\x91\x11\x00\x00'")))
	
	


def main():
	# get_ps_data(psnode38)
	# get_single_cs_data_py38(counter38_100)
	# get_single_cs_data_py37(counter37_1000_7_5)
	# get_single_cs_data_py37_con_interval()
	# get_4_cs_data_py37(four37_200)
	get_4_cs_data_py37_con_interval(four37_200_30)
	# plot_perfwriter(five37_100)  
	# plot_eight_device('030621_102316')
	# restore_raw_data()

if __name__ == "__main__":
	main()

