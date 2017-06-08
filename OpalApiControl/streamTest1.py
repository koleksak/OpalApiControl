from OpalApiControl.system import acquire
from OpalApiControl.OpalApiFormat import stream
from time import sleep

if __name__ == '__main__':
    print("running file streamTest1")
    #Connect to Dime Server
    stream.set_dime_connect('SE', 'tcp://127.0.0.1:5678')
    sleep(1)
    acquire.connectToModelTest('ephasorFormat1','phasor01_IEEE39')
    groups = (1, 2, 3)
    stream.stream_data(groups)
    stream.acq_data()
    stream.ltb_stream()
