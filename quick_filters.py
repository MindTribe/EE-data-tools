# Some quick, premade filter blocks for signal processing. Audacity has many useful filters available, but it does not
# fit well into an automated workflow.


import numpy
from scipy.signal import butter, lfilter, firwin, kaiserord

import load_and_show


# Quick FIR lowpass filter
# The filter uses simple math that can be easily ported to embedded systems that may not want to use floating point
# First block number of values are unfiltered, so this filter requires a settling time
def running_avg(vector, block=4):
    filtered_vector = numpy.zeros(len(vector))
    for i in xrange(len(vector)):
        for j in xrange(min(block, i + 1)):
            filtered_vector[i] += vector[i - j]
        filtered_vector[i] /= min(i + 1, block)
    return filtered_vector


# Quick IIR lowpass filter
# The filter uses simple math that can easily be ported to embedded systems
def exponential_filter(vector, alpha=0.8):
    filtered_vector = numpy.zeros(len(vector))
    filtered_vector[0] = vector[0]
    for i in xrange(1, len(vector)):
        filtered_vector[i] = alpha * vector[i] + (1 - alpha) * filtered_vector[i - 1]
    return filtered_vector


# From scipy cookbook
def butter_bandpass_filter(vector, lowcut, highcut, sample_rate, order=1):
    nyq = sample_rate / 2.0
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    filtered_vector = lfilter(b, a, vector)
    return filtered_vector

#------------------------------------------------
# Create a FIR filter and apply it to x.
# from scipy cookbook
#------------------------------------------------

def fir_lowpass(vector, sample_rate, cutoff_hz):
    # The Nyquist rate of the signal.
    nyq_rate = sample_rate / 2.0

    # The desired width of the transition from pass to stop,
    # relative to the Nyquist rate.  We'll design the filter
    # with a 5 Hz transition width.
    width = 5.0/nyq_rate
    
    # The desired attenuation in the stop band, in dB.
    ripple_db = 60.0
    
    # Compute the order and Kaiser parameter for the FIR filter.
    N, beta = kaiserord(ripple_db, width)
    
    # The cutoff frequency of the filter.
    #cutoff_hz = 10.0
    
    # Use firwin with a Kaiser window to create a lowpass FIR filter.
    taps = firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    
    # Use lfilter to filter x with the FIR filter.
    filtered_x = lfilter(taps, 1.0, vector)
    return filtered_x

    

if __name__ == "__main__":
    test = [1, 2, 3, 4, 5, 4, 6, 3, 7, 2, 9, 10, 8, 8, 8, 8, 8]
    time_test = range(len(test))
    f1 = running_avg(test, 4)
    f2 = exponential_filter(test, 0.4)
    f3 = butter_bandpass_filter(test, 1, 40, 100, 10)
    data = time_test
    data = numpy.column_stack((time_test, test, f1, f2, f3))
    load_and_show.show_data(data)
