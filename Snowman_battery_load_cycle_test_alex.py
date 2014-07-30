# Test script to cycle the electronic load, as if it were the motor, to determine maximum usage duty cycles

#sampling: during discharge: at least 1 sample per current step (taken just before the current is changed), log current value and voltage value
# sample every half second during discharge. Sample every minute when charging. 
# start a new file after the battery fully recharges. So each file should show charged=>discharge=>charge

import Agilent_6060B
import time
import u3
import csv
import os

#global constants
FINAL_CURRENT = 4.0
INITIAL_CURRENT = 1.0
ON_DURATION = 3.0
SLEEP_DURATION = 0.5
#number of sleep cycles (of duration SLEEP_DURATION) in which battery is allowed to recover between discharge cycles
RECOVER_SLEEP_CYCLES = 18 
CHARGE_SAMPLING_PERIOD = 60
MIN_VOLTAGE = float(3.7)
CHARGED_VOLTAGE = float(3.75)
SWITCH_GATE_OFF_VOLTAGE = 5
SWITCH_GATE_ON_VOLTAGE = 0
DAC_REGISTER = 5000

def WriteRow(csvWriter, entryList):
	csvWriter.writerow(entryList)

def TurnOnCurrent(handle, current, sleepDuration):
	#print "Set current to " + str(current) + " for " + str(duration) + " seconds"
	handle.set_current(current)
	handle.turn_on()
	time.sleep(sleepDuration)
	#handle.turn_off()

def RampUpCurrent(handle, initialCurrent, finalCurrent, onDuration, sleepDuration, recoverSleepCycles, startTime, csvWriter, dischargeCycle):
	t = 0
	handle.turn_on()
	#write data when current is 0
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

def TurnOffCurrent(handle):
	handle.turn_off()

def ReadVoltage(handle):
	return float(handle.measure_voltage())

def main():
	print "Connecting to Agilent 6060B"
	load_handle = Agilent_6060B.Agilent6060B()
	load_handle.connect()
	load_handle.get_info()
	load_handle.set_mode(load_handle.MODE_CURRENT)
	i = 0

	#configure labjack
	d = u3.U3()
	#set up Analog Output DAC0
	d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)

	#set initial time
	startTime = time.time()

	#create output base filename (YYYYMMDDHHMMSS)
	outputBaseFilename = time.strftime("%Y%m%d") + '-' + time.strftime("%H%M%S")
	#create directory for output files
	os.mkdir(outputBaseFilename)
	#create summary file
	summaryFile = open(os.path.join(outputBaseFilename, 'summary.csv'), 'wb')
	summaryWriter = csv.writer(summaryFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
	WriteRow(summaryWriter, ['Charge Cycle', 'Number of Discharge Cycles'])

	chargeCycle = 1
	while True:
		outputFile = open(os.path.join(outputBaseFilename, 'charge-cycle-' + str(chargeCycle) + '.csv'), 'wb')
		writer = csv.writer(outputFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
		WriteRow(writer, ['Time (s)', 'Voltage (V)', 'Current (A)', 'Phase', 'Discharge Cycle'])
		dischargeCycle = 1
		print "charge cycle no " + str(chargeCycle)
		while float(ReadVoltage(load_handle)) >= MIN_VOLTAGE:
			print "discharge cycle no " + str(dischargeCycle)
			RampUpCurrent(load_handle, INITIAL_CURRENT, FINAL_CURRENT, ON_DURATION, SLEEP_DURATION, RECOVER_SLEEP_CYCLES, startTime, writer, dischargeCycle)
			print "recover voltage = " + str(ReadVoltage(load_handle))
			print "____________________________"
			dischargeCycle += 1
		TurnOffCurrent(load_handle)
		WriteRow(summaryWriter, [chargeCycle, dischargeCycle])
		while float(ReadVoltage(load_handle)) < CHARGED_VOLTAGE:
				d.writeRegister(DAC_REGISTER, SWITCH_GATE_ON_VOLTAGE)
				WriteRow(writer, [time.time()-startTime, ReadVoltage(load_handle), None, 'charge', None])
				print ReadVoltage(load_handle)
				time.sleep(CHARGE_SAMPLING_PERIOD)
		d.writeRegister(DAC_REGISTER, SWITCH_GATE_OFF_VOLTAGE)
		chargeCycle += 1

if __name__ == '__main__':
    main()
