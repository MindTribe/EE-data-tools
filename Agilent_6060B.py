# http://prologix.biz/downloads/pxread.py
# http://cp.literature.agilent.com/litweb/pdf/5951-2826.pdf

import serial
import time

GPIB_ADDRESS = 5

# should probably be inherited, abstracted, or somehow derived from the Prologix GPIB controller.
class Agilent6060B:

    MODE_CURRENT = 'CURR'
    MODE_VOLTAGE = 'VOLT'
    MODE_RESISTANCE = 'RES'

    def __init__(self):
        self.serial_handle = None

    def connect(self):
        # Set up USB to GPIB as per Prologix instructions
        self.serial_handle = serial.Serial('/dev/tty.usbserial-PXWYFRKG', baudrate=9600, timeout=0.1)
        self.serial_handle.write('++mode 1\n')
        self.serial_handle.read(256)
        self.serial_handle.write('++addr 5\n')
        self.serial_handle.read(256)

    def get_info(self):
        #Quick comm with device
        self.serial_handle.write('*IDN?\n')
        print self.serial_handle.read(256)
        
    def set_voltage(self, voltage=5):
        self.serial_handle.write('VOLT ' +str(voltage)+'\n')
        self.serial_handle.read(256)

    def set_resistance(self, voltage=1000):
        self.serial_handle.write('RES ' +str(voltage)+'\n')
        self.serial_handle.read(256)

    def set_current(self, current=0.1):
        self.serial_handle.write('CURR ' +str(current)+'\n')
        self.serial_handle.read(256)

    def set_mode(self, mode=MODE_RESISTANCE):
        self.serial_handle.write('MODE:' + mode + '\n')
        self.serial_handle.read(256)
    
    #def set_slew(self, slew=0):
    #    self.serial_handle.write('SLEW ' + str(slew)+'\n')
    #    self.serial_handle.read(256)

    def turn_on(self):
        self.serial_handle.write('INPUT ON\n')
        self.serial_handle.read(256)

    def turn_off(self):
        self.serial_handle.write('INPUT OFF\n')
        self.serial_handle.read(256)

    def measure_voltage(self):
        self.serial_handle.write('MEAS:VOLT?\n')
        #print "voltage = " + str(self.serial_handle.read(256))
        VoltageMeasurement = self.serial_handle.read(256)
        return VoltageMeasurement

    def measure_voltage_now(self):
        self.serial_handle.write('MEAS:VOLT?\n')
        print "voltage = " + str(self.serial_handle.read(256))
        

if __name__ == '__main__':
    load_handle = Agilent6060B()
    load_handle.connect()
    load_handle.get_info()
    load_handle.set_mode(load_handle.MODE_CURRENT)
    #load_handle.set_resistance(1000)
    #load_handle.set_voltage(10)
    #load_handle.set_current(0.1)
    load_handle.turn_on()
    print "on"
    time.sleep(2)
    print 'off'
    load_handle.turn_off()
