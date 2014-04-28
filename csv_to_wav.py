#Starting code from https://gist.github.com/Pretz/1773870

# Audacity is a great tool for doing a lot of quick data analysis. As much of the data from our oscilloscopes is saved
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

#
MAX_AMPLITUDE = 32767


def prep_data_for_wav(data):
    for col in xrange(1, data.shape[1]):
        data[:, col] /= numpy.max(data[:, col])
        data[:, col] *= MAX_AMPLITUDE
        data[:, col] = data[:, col].astype('i16')
    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to load')
    args = parser.parse_args()
    data = load_and_show.load_csv(args.filename)
    print "Generating wave file from %d samples" % (len(data),)
    data = prep_data_for_wav(data)
    filename_head, extension = args.filename.rsplit(".", 1)
    data_samplerate = 1.0 / (data[1, 0] - data[0, 0])
    write_wav(data[:, 1], filename_head + ".wav", data_samplerate)