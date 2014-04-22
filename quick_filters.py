import numpy
import load_and_show
import argparse

#Quick FIR filter lowpass filter
# First block number of values are unfiltered. This can be updated with a better solution later
def running_avg(vector, block=4):
    filtered_data = numpy.zeros(len(vector))
    print range(0)
    print range(1)
    print range(2)
    for i in xrange(len(vector)):
        for j in xrange(min(block, i+1)):
            filtered_data[i] += vector[i - j]
        filtered_data[i] /= min(i+1, block)
    #print filtered_data
    return filtered_data

#Quick IIR lowpass filter
def exponential_filter(vector, alpha=0.8):
    filtered_data = numpy.zeros(len(vector))
    filtered_data[0] = vector[0]
    for i in xrange(1,len(vector)):
        filtered_data[i] = alpha * vector[i] + (1-alpha) * filtered_data[i-1]
    #print filtered_data
    return filtered_data

if __name__ == "__main__":
    test = [1,2,3,4,5,4,6,3,7,2,9,10,8,8,8,8,8]
    time_test = range(len(test))
    avg1 = running_avg(test,4)
    avg2 = exponential_filter(test, 0.4)
    data = time_test
    data = numpy.column_stack((time_test, test, avg1, avg2))
    load_and_show.show_data(data)
