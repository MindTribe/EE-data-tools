# Some quick, premade filter blocks for signal processing


import numpy
from scipy.signal import butter, lfilter

import load_and_show



# Quick FIR filter lowpass filter
# The filter uses simple math that can be easily ported to embedded systems that may not want to use floating point
# First block number of values are unfiltered, so this filter requires a settling time
def running_avg(vector, block=4):
    filtered_data = numpy.zeros(len(vector))
    for i in xrange(len(vector)):
        for j in xrange(min(block, i + 1)):
            filtered_data[i] += vector[i - j]
        filtered_data[i] /= min(i + 1, block)
    return filtered_data


# Quick IIR lowpass filter
# The filter uses simple math that can easily be ported to embedded systems
def exponential_filter(vector, alpha=0.8):
    filtered_data = numpy.zeros(len(vector))
    filtered_data[0] = vector[0]
    for i in xrange(1, len(vector)):
        filtered_data[i] = alpha * vector[i] + (1 - alpha) * filtered_data[i - 1]
    return filtered_data


# From scipy cookbook
# The filter
def butter_bandpass_filter(vector, lowcut, highcut, sample_rate, order=1):
    nyq = sample_rate / 2.0
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    filtered_data = lfilter(b, a, vector)
    return filtered_data


if __name__ == "__main__":
    test = [1, 2, 3, 4, 5, 4, 6, 3, 7, 2, 9, 10, 8, 8, 8, 8, 8]
    time_test = range(len(test))
    f1 = running_avg(test, 4)
    f2 = exponential_filter(test, 0.4)
    f3 = butter_bandpass_filter(test, 1, 40, 100, 10)
    data = time_test
    data = numpy.column_stack((time_test, test, f1, f2, f3))
    load_and_show.show_data(data)
