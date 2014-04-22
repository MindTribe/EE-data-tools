import argparse
import numpy
import matplotlib.pyplot as plt

def load_csv(filename):
    data = numpy.genfromtxt(filename, delimiter=',',skip_header=1)
    return data

# CSV is expected to have data labels in the first row, and data in all other rows
def show_data(data):
    print data
    plt.plot(data[:,0], data[:,1:])
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-f', '--filename', dest='filename', help='Name of the CSV file to load')
    args = parser.parse_args()
    show_data(load_csv(args.filename))
