#quick functions for looking at the frequency domain of a signal

import scipy

# quick fft of signal, returns array of Frequencies and FFT values 
def getFFT(signal, Fs):
    n = len(signal)
    d = 1/Fs
    FFT = abs(scipy.fft(signal))
    freqs = scipy.fftpack.fftfreq(n, d)
    return [freqs[:n/2],  FFT[:n/2]]

if __name__ == "__main__":
	t = scipy.linspace(0,120,4000)
	acc = lambda t: 10*scipy.sin(2*pi*2.0*t) + 5*scipy.sin(2*pi*8.0*t) + 2*scipy.random.random(len(t))
	signal = acc(t)
	getFFT(signal, t[1] - t[0]	)
	pylab.subplot(211)
	pylab.plot(signal)
	pylab.subplot(212)
	pylab.plot(x,20*scipy.log10(y),'x')
	pylab.show()

