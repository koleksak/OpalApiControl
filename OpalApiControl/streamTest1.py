from OpalApiControl.config import *
from acquisition import streamdev
import csv

if __name__ == '__main__':
    print("running file streamTest1")
    acquire.connectToModelTest('ephasorFormat1','phasor01_IEEE39')
    groups = (1, 2, 3)
    streamdev.stream_data(groups)

