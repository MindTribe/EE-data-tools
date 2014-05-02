# Fails on Mac unless 32-bit version is used. As EE's have 32-bit Python 2.7 on windows, starting project windows only.
# More Mac info here http://bardagjy.com/?p=1245
#from pyvisa.vpp43 import visa_library
#visa_library.load_library("/Library/Frameworks/Visa.framework/VISA")

#http://cp.literature.agilent.com/litweb/pdf/E3631-90002.pdf
#https://media.readthedocs.org/pdf/pyvisa/latest/pyvisa.pdf

import visa
import time


class AgilentE3631A(object):
    CHANNEL_P6V = 'P6V'
    CHANNEL_P25V = 'P25V'
    CHANNEL_N25V = 'N25V'

    def __init__(self):
        self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self.handle = visa.SerialInstrument('COM7', baud_rate=9600, parity=visa.no_parity, data_bits=8, stop_bits=1)
        self.handle.term_chars = '\r\n'

        # Unsure why, but writing a newline is in the example code
        self.handle.write('\n')
        # Take control
        self.handle.write('SYST:REM')
        # Reset and clear
        self.handle.write('*RST; *CLS')
        # Give time for the system to stabilize
        time.sleep(5)

    def disconnect(self):
        self.all_channels_off()
        # return control to panel
        self.handle.write('SYST:LOC')
        self.handle.close()

    def get_info(self):
        print 'System Version ' + self.handle.ask('SYST:VERS?')
        print 'System ID ' + self.handle.ask('*IDN?')

    def all_channels_on(self):
        self.handle.write('OUTPUT:STAT ON')

    def all_channels_off(self):
        self.handle.write('OUTPUT:STAT OFF')

    #Does not work
    def measure(self):
        print self.handle.write('MEAS:VOLT? ' + self.CHANNEL_P25V)

    def set_channel(self, channel=None, voltage_limit=1.0, current_limit=0.1):
        self.handle.write('APPL ' + channel + ',' + str(voltage_limit) + ',' + str(current_limit))

# Command line interface shown as an example.
if __name__ == "__main__":
    import numpy as np

    START_VOLTAGE = 3.0
    END_VOLTAGE = 3.6
    RANGE_VOLTAGE = 5
    CURR_LIMIT = 0.1
    STABLE_TIME = 5

    power_supply = AgilentE3631A()
    power_supply.get_info()
    for volt in np.linspace(START_VOLTAGE, END_VOLTAGE, RANGE_VOLTAGE, endpoint=True):
        power_supply.set_channel(power_supply.CHANNEL_P25V, voltage_limit=volt, current_limit=CURR_LIMIT)
        power_supply.all_channels_on()
        time.sleep(STABLE_TIME)