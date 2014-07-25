# Test script to cycle the electronic load, as if it were the motor, to determine maximum usage duty cycles

import Agilent_6060B
import time

FINAL_CURRENT = 4.0
INITIAL_CURRENT = 1.0
ON_DURATION = 3.0
SLEEP_DURATION = 0.5
OFF_DURATION = 9.0
MIN_VOLTAGE = float(3.7)

def TurnOnCurrent(handle, current, sleepDuration):
	#print "Set current to " + str(current) + " for " + str(duration) + " seconds"
	handle.set_current(current)
	handle.turn_on()
	time.sleep(sleepDuration)
	#handle.turn_off()

def RampUpCurrent(handle, initialCurrent, finalCurrent, onDuration, sleepDuration, offDuration):
	t = 0
	handle.turn_on()
	while (t <= onDuration):
		current = (initialCurrent + ((finalCurrent - initialCurrent)/onDuration)*t)
		handle.set_current(current)
		print "Set current to " + str(current)
		t += sleepDuration
		time.sleep(sleepDuration)
	handle.measure_voltage_now()
	handle.set_current(0)
	print "Set current to 0.0"
	time.sleep(offDuration)

def TurnOffCurrent(handle):
	handle.turn_off()

def ReadVoltage(handle):
	return handle.measure_voltage()

def main():
	print "Connecting to Agilent 6060B"
	load_handle = Agilent_6060B.Agilent6060B()
	load_handle.connect()
	load_handle.get_info()
	load_handle.set_mode(load_handle.MODE_CURRENT)
	i = 0
	while float(ReadVoltage(load_handle)) >= MIN_VOLTAGE:
		print "test cycle no " + str(i+1)
		RampUpCurrent(load_handle, INITIAL_CURRENT, FINAL_CURRENT, ON_DURATION, SLEEP_DURATION, OFF_DURATION)
		print "recover voltage = " + str(ReadVoltage(load_handle))
		print "____________________________"
		i += 1
	TurnOffCurrent(load_handle)

if __name__ == '__main__':
    main()
