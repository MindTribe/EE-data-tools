# Fails on Mac unless 32-bit version is used. As EE's have 32-bit Python 2.7 on windows, starting project windows only.
# More Mac info here http://bardagjy.com/?p=1245
#from pyvisa.vpp43 import visa_library
#visa_library.load_library("/Library/Frameworks/Visa.framework/VISA")

#http://cp.literature.agilent.com/litweb/pdf/E3631-90002.pdf
#https://media.readthedocs.org/pdf/pyvisa/latest/pyvisa.pdf

import visa
import time


def connect():
    #rm = visa.ResourceManager()
    print visa.get_instruments_list()
    my_instrument = visa.SerialInstrument('COM7',baud_rate=9600, parity=visa.no_parity, data_bits=8, stop_bits=1)
    my_instrument.timeout = 10
    my_instrument.term_chars = '\r\n'
    my_instrument.write('\n')
    my_instrument.write("SYST:REM")
    print "remote control"
    time.sleep(3)
    my_instrument.write("*RST; *CLS")
    print "reset and clear"
    time.sleep(5)
    print 'get version'
    print my_instrument.ask("SYST:VERS?")
    print my_instrument.ask('*IDN?')
    my_instrument.close()

if __name__ == "__main__":
    connect()