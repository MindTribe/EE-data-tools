# Test script to cycle the electronic load, as if it were the motor, to determine maximum usage duty cycles for a battery. 
# Samples battery current and voltage and outputs results to csv files.
# Before running the script, you should set the CURRENT_PROFILE variable, which is a list of ordered pairs that specify
# (currentToBeApplied, duration). For example, if you want to apply 1A for 1s, then 0A for 10s, set 
# CURRENT_PROFILE = [(1,0), (0,10)]

import Agilent_6060B
import time
import u3
import csv
import os
import math 

#global constants
#list of ordered pairs that specify (currentToBeApplied, duration). 
CURRENT_PROFILE = [(3.5, 0.5), (2.5, 1.5), (1, 0.5), (3.5, 0.5), (0, 2), (0.6, 4), (0, 50)]
#voltage at which battery is considered drained
MIN_VOLTAGE = float(3.7)
#voltage at which battery is considered charged
CHARGED_VOLTAGE = float(4.1)
DISCHARGE_SAMPLING_PERIOD = 0.5
CHARGE_SAMPLING_PERIOD = 60
SWITCH_GATE_OFF_VOLTAGE = 5
SWITCH_GATE_ON_VOLTAGE = 0
DAC_REGISTER = 5000
ANALOG_INPUT_REGISTER = 2
#note that this is an empirical approximation of the time it takes to set the current on the electronic load. 
PROGRAMMING_DELAY = 0.5

def WriteRow(csvWriter, entryList):
	csvWriter.writerow(entryList)

def ApplyCurrentProfile(handle, labJackHandle, currentProfile, startTime, csvWriter, dischargeCycle):
	#currentProfile should be a list of tuples which represent ordered pairs of (currentToBeApplied, duration).
	handle.turn_on()
	#write before current ramping
	WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(labJackHandle), 0, 'discharge', dischargeCycle])
	for pairNumber, pair in enumerate(currentProfile):
		current = pair[0]
		duration = pair[1]
		#assume that setting the current takes PROGRAMMING_DELAY seconds
		handle.set_current(current)
		print 'Set current to %f' % current
		voltage = ReadVoltage(labJackHandle)
		if pairNumber is len(currentProfile) - 1:
			WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'recover', dischargeCycle])
		else:
			WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'discharge', dischargeCycle])
		numSamples = int(math.floor((duration-PROGRAMMING_DELAY)/DISCHARGE_SAMPLING_PERIOD))
		for sample in range(numSamples):
			time.sleep(DISCHARGE_SAMPLING_PERIOD)
			voltage = ReadVoltage(labJackHandle)
			if pairNumber is len(currentProfile) - 1:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'recover', dischargeCycle])
			else:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'discharge', dischargeCycle])

def ReadVoltage(labJackHandle):
	#multiply by two to account for the resistive divider (which is necessary since the labjack's full scale range is only 0-2.4V)
	return 2*labJackHandle.readRegister(ANALOG_INPUT_REGISTER)

def main():
	#bounds check on CURRENT_PROFILE durations
	for pair in CURRENT_PROFILE:
		if pair[1] < PROGRAMMING_DELAY:
			raise Exception('ERROR: all durations in CURRENT_PROFILE must be greater than %f. This is the minimum time required to set current on the electronic load.' % PROGRAMMING_DELAY)

	#configure electronic load
	print 'Connecting to Agilent 6060B'
	load_handle = Agilent_6060B.Agilent6060B()
	load_handle.connect()
	#load_handle.get_info()
	load_handle.set_mode(load_handle.MODE_CURRENT)

	#configure labjack
	print 'Connecting to LabJack'
	d = u3.U3()
	#set up Analog Output DAC0
	d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)
	d.configIO(FIOAnalog = 2) # Set FIO1 to analog

	#set initial time
	startTime = time.time()

	#create output base filename (YYYYMMDD-HHMMSS)
	outputBaseFilename = 'battery-cycle-test-' + time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S")

	#create directory for output files
	os.mkdir(outputBaseFilename)

	#create summary file
	summaryFile = open(os.path.join(outputBaseFilename, 'summary.csv'), 'wb')
	summaryWriter = csv.writer(summaryFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	WriteRow(summaryWriter, ['Charge Cycle', 'Number of Discharge Cycles'])

	chargeCycle = 0
	while True:
		chargeCycle += 1
		#create output file
		outputFile = open(os.path.join(outputBaseFilename, 'charge-cycle-%d.csv' % chargeCycle), 'wb')
		writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		WriteRow(writer, ['Time (s)', 'Voltage (V)', 'Current (A)', 'Phase', 'Discharge Cycle'])
		dischargeCycle = 0
		print '\nCharge cycle: %d' % chargeCycle
		while ReadVoltage(d) >= MIN_VOLTAGE:
			dischargeCycle += 1
			print '\nDischarge cycle: %d' % dischargeCycle
			ApplyCurrentProfile(load_handle, d, CURRENT_PROFILE, startTime, writer, dischargeCycle)
			print 'Recover voltage: %f' % ReadVoltage(d)
			print '____________________________'
		load_handle.set_current(0)
		load_handle.turn_off
		WriteRow(summaryWriter, [chargeCycle, dischargeCycle])
		while ReadVoltage(d) < CHARGED_VOLTAGE:
				d.writeRegister(DAC_REGISTER, SWITCH_GATE_ON_VOLTAGE)
				WriteRow(writer, [time.time()-startTime, ReadVoltage(d), None, 'charge', None])
				print ReadVoltage(d)
				time.sleep(CHARGE_SAMPLING_PERIOD)
		d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)

if __name__ == '__main__':
    main()
