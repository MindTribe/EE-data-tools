# Test script to cycle the electronic load, as if it were the motor, to determine maximum usage duty cycles for a battery. 
# Samples battery current and voltage and outputs results to csv files.

import Agilent_6060B
import time
import u3
import csv
import os
import math 

#global constants
FINAL_CURRENT = 4.0
INITIAL_CURRENT = 1.0
ON_DURATION = 3.0
SLEEP_DURATION = 0.5
#number of sleep cycles (of duration SLEEP_DURATION) in which battery is allowed to recover between discharge cycles
RECOVER_SLEEP_CYCLES = 18 
CHARGE_SAMPLING_PERIOD = 60
MIN_VOLTAGE = float(3.7)
CHARGED_VOLTAGE = float(3.8)
SWITCH_GATE_OFF_VOLTAGE = 5
SWITCH_GATE_ON_VOLTAGE = 0
DAC_REGISTER = 5000
ANALOG_INPUT_REGISTER = 2
CURRENT_PROFILE = [(1.5, 3), (3.5, 1), (0, 1), (1, 1), (0, 1), (3.5, 3), (0, 20)]
SAMPLING_PERIOD = 0.5

def WriteRow(csvWriter, entryList):
	csvWriter.writerow(entryList)

def TurnOnCurrent(handle, current, sleepDuration):
	handle.set_current(current)
	handle.turn_on()
	time.sleep(sleepDuration)

def RampUpCurrent(handle, initialCurrent, finalCurrent, onDuration, sleepDuration, recoverSleepCycles, startTime, csvWriter, dischargeCycle):
	t = 0
	handle.turn_on()
	#write before current ramping
	WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(handle), 0, 'discharge', dischargeCycle])
	while (t <= onDuration):
		current = (initialCurrent + ((finalCurrent - initialCurrent)/onDuration)*t)
		handle.set_current(current)
		print "Set current to " + str(current)
		t += sleepDuration
		time.sleep(sleepDuration)
		WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(handle), current, 'discharge', dischargeCycle])
	handle.measure_voltage_now()
	handle.set_current(0)
	print "Set current to 0.0"
	for i in range(recoverSleepCycles):
		WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(handle), 0, 'recover', dischargeCycle])
		time.sleep(sleepDuration)

def ApplyCurrentProfile(handle, labJackHandle, currentProfile, startTime, csvWriter, dischargeCycle):
	#currentProfile should be a list of tuples which represent ordered pairs of (currentToBeApplied, duration).
	handle.turn_on()
	#write before current ramping
	WriteRow(csvWriter, [time.time()-startTime, ReadVoltage(labJackHandle), 0, 'discharge', dischargeCycle])
	for pairNumber, pair in enumerate(currentProfile):
		current = pair[0]
		duration = pair[1]
		numSamples = int(math.floor(duration/SAMPLING_PERIOD))
		for sample in range(numSamples):
			tic = time.time()
			if sample is 0:
				handle.set_current(current)
				print "Set current to " + str(current)
			toc = time.time()
			time.sleep(max(0, SAMPLING_PERIOD - (toc-tic)))
			voltage = ReadVoltage(labJackHandle)
			if pairNumber is len(currentProfile) - 1:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'recover', dischargeCycle])
			else:
				WriteRow(csvWriter, [time.time()-startTime, voltage, current, 'discharge', dischargeCycle])

def TurnOffCurrent(handle):
	handle.turn_off()

def ReadVoltage(labJackHandle):
	#multiply by two to account for the resistive divider (which is necessary since the labjack's full scale range is only 0-2.4V)
	return 2*labJackHandle.readRegister(ANALOG_INPUT_REGISTER)

def main():
	#configure electronic load
	print "Connecting to Agilent 6060B"
	load_handle = Agilent_6060B.Agilent6060B()
	load_handle.connect()
	load_handle.get_info()
	load_handle.set_mode(load_handle.MODE_CURRENT)

	#configure labjack
	d = u3.U3()
	#set up Analog Output DAC0
	d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)
	d.configIO(FIOAnalog = 2) # Set FIO1 to analog

	#set initial time
	startTime = time.time()

	#create output base filename (YYYYMMDD-HHMMSS)
	outputBaseFilename = time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S")

	#create directory for output files
	os.mkdir(outputBaseFilename)

	#create summary file
	summaryFile = open(os.path.join(outputBaseFilename, 'summary.csv'), 'wb')
	summaryWriter = csv.writer(summaryFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	WriteRow(summaryWriter, ['Charge Cycle', 'Number of Discharge Cycles'])

	chargeCycle = 1
	while True:
		#create output file
		outputFile = open(os.path.join(outputBaseFilename, 'charge-cycle-' + str(chargeCycle) + '.csv'), 'wb')
		writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		WriteRow(writer, ['Time (s)', 'Voltage (V)', 'Current (A)', 'Phase', 'Discharge Cycle'])
		dischargeCycle = 1
		print "charge cycle: " + str(chargeCycle)
		while float(ReadVoltage(d)) >= MIN_VOLTAGE:
			print "discharge cycle: " + str(dischargeCycle)
			ApplyCurrentProfile(load_handle, d, CURRENT_PROFILE, startTime, writer, dischargeCycle)
			print "recover voltage = " + str(ReadVoltage(d))
			print "____________________________"
			dischargeCycle += 1
		TurnOffCurrent(load_handle)
		WriteRow(summaryWriter, [chargeCycle, dischargeCycle])
		while float(ReadVoltage(d)) < CHARGED_VOLTAGE:
				d.writeRegister(DAC_REGISTER, SWITCH_GATE_ON_VOLTAGE)
				WriteRow(writer, [time.time()-startTime, ReadVoltage(d), None, 'charge', None])
				print ReadVoltage(d)
				time.sleep(CHARGE_SAMPLING_PERIOD)
		d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)
		chargeCycle += 1

if __name__ == '__main__':
    main()
