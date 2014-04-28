# CSVs are a common output of our equipment. These functions are commonly used when opening a CSV file

import argparse

import numpy
import matplotlib.pyplot as plt


# Function takes a CSV filename and returns a numpy array. The first row is expected to be a header
def load_csv(filename):
    data = numpy.genfromtxt(filename, delimiter=',', skip_header=1)
    return data


# Data column 0 is assumed to be time, or another independent variable. All other columns are assumed to be dependant
def show_data(data):
    plt.plot(data[:, 0], data[:, 1:])
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to load')
    args = parser.parse_args()
    show_data(load_csv(args.filename))
