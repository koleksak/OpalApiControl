# This sets data into a data list, and retrieves the data after every entry depending on the model sampling rate.
from config import *
print("in File threadTest1")
if __name__ == '__main__':
    print("running file ThreadTest1")
    dataStruc1 = acquisitioncontrol.DataList(1);
    dirset = acquisitioncontrol.StartAcquisitionThread('ephasorex2','phasor01_IEEE39',dataStruc1,1,"AcqThread Set",1)
    dirret = acquisitioncontrol.acquisitionThreadReturn('ephasorex2','phasor01_IEEE39',dataStruc1,1,"AcqThread Return",1)
    dirret.setDaemon(True)
    dirset.start()
    dirret.start()
    #Joining seems to function better if you wait for thread to start
    sleep(3)
    dirset.join(2)
    dirret.join(2)
