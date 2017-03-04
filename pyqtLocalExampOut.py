from OpalApiControl.config import *
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import csv

import collections
import random
import time
import math
import numpy as np
#
dataStruct1 = acquisitioncontrol.DataList(1)
structSet = acquisitioncontrol.StartAcquisitionThread('ephasorDataPlotOut','phasor01_IEEE39',dataStruct1,1,"AcqThread Set",1)
structRet = acquisitioncontrol.acquisitionThreadReturnWithTime('ephasorDataPlotOut','phasor01_IEEE39',dataStruct1,1,"AcqThread Ret",0.033)
structSet.start()
structRet.start()
#sleep(1)

class DynamicPlotter():

    def __init__(self, sampleinterval=1., timewindow=100., size=(600,350)):
        # Data stuff
        #threading.Thread.__init__(self)
        self.sample = 0
        self.Xwindow = timewindow
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer1 = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer2 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-self.Xwindow, 0, self._bufsize)
        self.y1 = np.zeros(self._bufsize, dtype=np.float)
        #self.y2 = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y1, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)
        count = 0
        self.count = count


    def getdata(self):


        #val = structRet.dataList.returnLastAcq()
        val = structRet.dataList.returnLastAcq()
        if (len(dataStruct1.dataValues) > 0):
            y1 = np.sin(val[12])
            #y2 = np.sin(val[13])
            #print"Y Value = %s" %y1
            #print"Y Value = %s" %y2
            return y1

    def updateplot(self):
        y1 = self.getdata()
        self.databuffer1.append(y1)
        #self.databuffer2.append(y2)
        self.y1[:] = self.databuffer1
        #self.y2[:] = self.databuffer2
        self.curve.setData(self.x, self.y1)
        self.sample += 1
        self.Xwindow += 1
        #self.plt.setXRange(self.sample, self.Xwindow)
        self.app.processEvents()


    def run(self):
        self.app.exec_()

if __name__ == '__main__':

    m = DynamicPlotter(sampleinterval=0.1, timewindow=10.)
    m.run()

