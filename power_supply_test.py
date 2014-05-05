import argparse
import numpy
import time

from picoscope import ps5000a
# import Agilent PS



if __name__ == "__main__":

    # Assuming a 2MHz switching f
    SAMPLING_F = 10E6
    VOLT_RESOLUTION = 5

    CHANNELS = ['A', 'B', 'C', 'D']

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to save',default='default.csv')
    parser.add_argument('--low_voltage', dest='low_v', help='Starting voltage for input sweep', default=None, type=float)
    parser.add_argument('--high_voltage', dest='high_v', help='Ending voltage for input sweep',default=None, type=float)
    parser.add_argument('--steps', dest='steps',help='Number of voltages tested between low and high', default=1, type=float)
    #parser.add_argument('--labels', dest='labels',help='Channel labels. Example   "Input_V,Output_V,Input_I"', default='')
    parser.add_argument('--channels', dest='channels', help='Number of channels. A=1, A and B = 2, etc...', default=1, type=int)
    args = parser.parse_args()

    scope = ps5000a.PS5000a(connect=False)
    serial = scope.enumerateUnits()
    #print serial

    scope = ps5000a.PS5000a(serial[0])
    #print scope.getAllUnitInfo()


    res = scope.setSamplingFrequency(SAMPLING_F, 4096)
    #print res
    sampleRate = res[0]
    print "Sampling @ %f MHz, %d samples"%(res[0]/1E6, res[1])

    #data = numpy.zeros(4096)
    data = numpy.array(0)
    for count in range(args.channels):
        scope.setChannel(CHANNELS[count], "DC", VOLT_RESOLUTION)
    for _ in xrange(5):
        scope.runBlock()
        while(scope.isReady() == False): time.sleep(0.01)
        a = scope.getDataV(CHANNELS[count], 4096)
        b = scope.getDataV(CHANNELS[count], 4096)
        data = zip(a,b)
        print data
        #data = numpy.append(data, [a,b])
        #for count in range(args.channels):
        #    data = numpy.column_stack((data, scope.getDataV(CHANNELS[count], 4096)))
            #print data.astype(int), data.shape

    #first sample seems to be extranously added
    #data = data[1:]
    #print data.shape
    #data = numpy.reshape(data,(-1,args.channels))


    #calculate time column
    times = numpy.arange(start=0,stop=data.shape[0],step=1,dtype=float)/res[0]

    data = numpy.column_stack((times,data))

    #supply = ...()

    #set up scope

    #set up supply

    #start recording

    #for volts in numpy.linspace(args.low_v, args.high_v, args.steps, endpoint=True):
        #change voltage
        #enable
    #    time.sleep(10)
        #disable

    scope.close()
    #break file into multiple parts, or add comment lines?
    header = 'Time'
    for count in xrange(args.channels):
        header = header + ',' + CHANNELS[count]

    #format numpy array
    numpy.savetxt(fname=args.filename , X=data, delimiter=',', header=header)




