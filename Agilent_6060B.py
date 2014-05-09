# http://prologix.biz/downloads/pxread.py
# http://cp.literature.agilent.com/litweb/pdf/5951-2826.pdf

import serial

GPIB_ADDRESS = 5


# should probably be inherited, or somehow derived, from the Prologix GPIB controller.
class Agilent6060B(object):

    def connect(self):
        serial_handle = serial.Serial('COM9', baudrate=9600, timeout=0.5)

        serial_handle.write('++mode 1\n')
        print serial_handle.read(256)

        serial_handle.write('++addr 5\n')
        print serial_handle.read(256)

        serial_handle.write('*IDN?\n')
        print serial_handle.read(256)

if __name__ == '__main__':
    load_handle = Agilent6060B()
    load_handle.connect()
