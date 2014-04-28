#Starting code from https://gist.github.com/Pretz/1773870

# Audacity is a useful tool for doing a lot of quick data analysis. As much of the data from oscilloscopes is saved
# in CSV format, having a tool to convert the data into a form Audacity can read can be useful.

import wave
import argparse
import struct

import numpy

import load_and_show



# Write one channel of 16bit integer data
def write_wav(data, filename, framerate):
    wavfile = wave.open(filename, "w")
    nchannels = 1
    sampwidth = 2
    framerate = framerate
    nframes = len(data)
    comptype = "NONE"
    compname = "not compressed"
    wavfile.setparams((nchannels,
                       sampwidth,
                       framerate,
                       nframes,
                       comptype,
                       compname))
    print("Please be patient whilst the file is written")
    frames = []
    for s in data:
        frames.append(struct.pack('h', s))
        print s
    frames = ''.join(frames)
    wavfile.writeframes(frames)
    wavfile.close()
    print("%s written" % filename)


MAX_WAV_AMPLITUDE = 32767


# Manipulate data that will be saved in the wav file. Column 0 is expected to be time, and therefore ignored.
# Each channel is scaled to maximum value per channel (cannot compare amplitude across channels).
def prep_data_for_wav(data):
    for col in xrange(1, data.shape[1]):
        data[:, col] /= numpy.max(data[:, col])
        data[:, col] *= MAX_WAV_AMPLITUDE
        data[:, col] = data[:, col].astype('i16')
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to load')
    args = parser.parse_args()
    data = load_and_show.load_csv(args.filename)
    print "Generating wave file from %d samples" % (len(data),)
    data = prep_data_for_wav(data)

    # make the output filename the same as the input
    filename_head, extension = args.filename.rsplit(".", 1)

    # Assuming the sample_rate is constant in the data and column 0 = time
    data_samplerate = 1.0 / (data[1, 0] - data[0, 0])

    # Time does not get written in the wav. Only data gets written. Time is accounted for in data_samplerate
    write_wav(data[:, 1], filename_head + ".wav", data_samplerate)