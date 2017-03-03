from OpalApiControl.config import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

import collections
import random
import time
import math
import numpy as np

dataStruct1 = acquisitioncontrol.DataList(1)
structSet = acquisitioncontrol.StartAcquisitionThread('ephasorex2','phasor01_IEEE39',dataStruct1,1,"AcqThread Set",1)
structRet = acquisitioncontrol.acquisitionThreadReturnWithTime('ephasorex2','phasor01_IEEE39',dataStruct1,1,"AcqThread Ret",0.1)
structSet.start()
structRet.start()
# sleep(5)


class DynamicPlotter():

    def __init__(self, sampleinterval=0.1, timewindow=100., size=(600,350)):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow*1000/sampleinterval)
        self.databuffer1 = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer2 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y1 = np.zeros(self._bufsize, dtype=np.float)
        self.y2 = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y1=True,y2=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y1,self.y2, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        #frequency = 0.5
        #noise = random.normalvariate(0., 1.)
        #new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
        val = structRet.lastAcq
        if(len(dataStruct1.dataValues) > 0):
            y1 = np.sin(val[12])
            y2 = np.sin(val[13])
            print"Y Value = %s" %y1
            print"Y Value = %s" %y2
            return y1, y2

    def updateplot(self):
        y1,y2 = self.getdata()
        self.databuffer1.append(y1)
        self.databuffer2.append(y2)
        self.y1[:] = self.databuffer1
        self.y2[:] = self.databuffer2
        self.curve.setData(self.x, self.y1,self.y2)
        self.app.processEvents()

    def run(self):
        self.app.exec_()

if __name__ == '__main__':

    m = DynamicPlotter(sampleinterval=0.1, timewindow=10.)
    m.run()
