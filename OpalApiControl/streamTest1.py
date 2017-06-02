from OpalApiControl.config import *
from acquisition import stream
import csv

if __name__ == '__main__':
    print("running file streamTest1")
    acquire.connectToModelTest('ephasorFormat1','phasor01_IEEE39')
    groups = (1, 2, 3)
    stream.stream_data(groups)

