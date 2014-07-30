import u3
import Agilent_6060B
import time

#This just checks how fast analog voltage read takes for the labjack vs the electronic load

d = u3.U3()
d.configIO(FIOAnalog = 2) # Set FIO1 to analog
register = 2
tic = time.time()
print str(2*d.readRegister(register))
toc = time.time()
print 'labjack analog read took: %f seconds' % (toc-tic)

	
load_handle = Agilent_6060B.Agilent6060B()
load_handle.connect()
load_handle.set_mode(load_handle.MODE_CURRENT)
tic = time.time()
print float(load_handle.measure_voltage())
toc = time.time()
print 'electronic load analog read took: %f seconds' % (toc-tic)


