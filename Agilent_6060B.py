# http://prologix.biz/downloads/pxread.py
# http://cp.literature.agilent.com/litweb/pdf/5951-2826.pdf

import serial

GPIB_ADDRESS = 5


# should probably be inherited, abstracted, or somehow derived from the Prologix GPIB controller.
class Agilent6060B(object):

    MODE_CURRENT = 'CURR'
    MODE_VOLTAGE = 'VOLT'
    MODE_RESISTANCE = 'RES'

    def connect(self):
        # Set up USB to GPIB
        self.serial_handle = serial.Serial('COM9', baudrate=9600, timeout=0.5)
        self.serial_handle.write('++mode 1\n')
        self.serial_handle.read(256)
        self.serial_handle.write('++addr 5\n')
        self.serial_handle.read(256)

        #Quick comm with device
        self.serial_handle.write('*IDN?\n')
        print self.serial_handle.read(256)
        
    def set_voltage(self, voltage=5):
        self.serial_handle.write('VOLT ' +str(voltage)+'\n')
        self.serial_handle.read(256)

    def set_resistance(self, voltage=1000):
        self.serial_handle.write('RES ' +str(voltage)+'\n')
        self.serial_handle.read(256)

    def set_mode(self, mode=MODE_RESISTANCE):
        self.serial_handle.write('MODE:' + mode + '\n')
        self.serial_handle.read(256)

    def turn_on(self):
        self.serial_handle.write('INPUT ON\n')
        self.serial_handle.read(256)

    def turn_off(self):
        self.serial_handle.write('INPUT OFF\n')
        self.serial_handle.read(256)

if __name__ == '__main__':
    load_handle = Agilent6060B()
    load_handle.connect()
    load_handle.set_mode()
    load_handle.set_resistance(1000)
    #load_handle.set_voltage(10)
    load_handle.turn_on()
