import argparse
import numpy
import time

import load_and_show

from picoscope import ps5000a
import Agilent_E3631A

if __name__ == "__main__":

    # Assuming a 2MHz switching f
    SAMPLING_F = 5E6
    VOLT_RESOLUTION = 5
    CHANNELS = ['A', 'B', 'C', 'D']

    # Command line parser
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to save',default='default.csv')
    parser.add_argument('--low_voltage', dest='low_v', help='Starting voltage for input sweep', default=3.0, type=float)
    parser.add_argument('--high_voltage', dest='high_v', help='Ending voltage for input sweep',default=3.1, type=float)
    parser.add_argument('--steps', dest='steps',help='Number of voltages tested between low and high', default=1, type=float)
    #parser.add_argument('--labels', dest='labels',help='Channel labels. Example   "Input_V,Output_V,Input_I"', default='')
    parser.add_argument('--channels', dest='channels', help='Number of channels. A=1, A and B = 2, etc...', default=1, type=int)
    args = parser.parse_args()

    # Start the hardware
    scope = ps5000a.PS5000a(connect=False)
    serial = scope.enumerateUnits()
    scope = ps5000a.PS5000a(serial[0])
    power_supply = Agilent_E3631A.AgilentE3631A()
    print scope.getAllUnitInfo()
    print power_supply.get_info()

    # Set up sampling resolution
    res = scope.setSamplingFrequency(SAMPLING_F, 4096)
    sampleRate = res[0]
    res = scope.setSamplingFrequency(SAMPLING_F, res[1]/4)
    print "Sampling @ %f MHz, %d samples"%(res[0]/1E6, res[1])

    # Set up each channel as a member of a dictionary
    input_channels = {'A' : numpy.array(0)}
    for count in xrange(args.channels):
        input_channels[CHANNELS[count]] = numpy.array(0)

    # set up scope channels
    scope.setResolution('12')
    for count in range(args.channels):
        scope.setChannel(CHANNELS[count], "DC", VOLT_RESOLUTION)


    # Run the acquisition loop
    for volts in numpy.linspace(start=args.low_v, stop=args.high_v, num=args.steps):
        scope.runBlock()
        power_supply.set_channel(power_supply.CHANNEL_P25V, voltage_limit=volts, current_limit=0.5)
        power_supply.all_channels_on()
        while(scope.isReady() == False): time.sleep(0.01)
        for count in range(args.channels):
            input_channels[CHANNELS[count]] = numpy.append(input_channels[CHANNELS[count]], scope.getDataV(CHANNELS[count], res[1]/4))
        power_supply.all_channels_off()


    # calculate time column
    # NOTE: There may be timing issues between each scope.runBlock() call. Need to confirm
    times = numpy.arange(start=0,stop=len(input_channels['A']),step=1,dtype=float)/res[0]

    # This could probably all be printed directly from the dictionary instead of stacking a numpy array
    data = input_channels['A']
    for count in xrange(1, args.channels):
        data = numpy.column_stack((data,input_channels[CHANNELS[count]]))
    data = numpy.column_stack((times,data))


    scope.close()
    power_supply.all_channels_off()
    # Create the header
    header = 'Time'
    for count in xrange(args.channels):
        header = header + ',' + CHANNELS[count]

    # Save as CSV
    #numpy.savetxt(fname=args.filename , X=data, delimiter=',', header=header)


    # See data
    load_and_show.show_data(data[::4,:])




