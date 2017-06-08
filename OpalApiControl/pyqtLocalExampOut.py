from OpalApiControl.acquisition import acquisitioncontrol
import threading
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import csv

import collections
import random
import time
import math
import numpy as np


# acquire.connectToModelTest('ephasorDataPlotOut','phasor01_IEEE39')
dataStruct1 = acquisitioncontrol.DataList(1)
structSet = acquisitioncontrol.StartAcquisitionThread('ephasorDataPlotOut','phasor01_IEEE39',dataStruct1,1,"AcqThread Set",0.03333)
#structRet = acquisitioncontrol.acquisitionThreadReturn('ephasorDataPlotOut','phasor01_IEEE39',dataStruct1,1,"AcqThread Ret",1)
#structSet.start()
#structRet.start()
#sleep(1)

class DynamicPlotter(threading.Thread,acquisitioncontrol.DataList):

    def __init__(self, sampleinterval=1., timewindow=100., size=(644,400)):
        # Data stuff
        threading.Thread.__init__(self)
        self.sample = 0
        self.Xwindow = timewindow
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer1 = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.databuffer2 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer3 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer4 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer5 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer6 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer7 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer8 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer9 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.databuffer10 = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(0,timewindow, self._bufsize)
        self.y1 = np.zeros(self._bufsize, dtype=np.float)
        self.y2 = np.zeros(self._bufsize, dtype=np.float)
        self.y3 = np.zeros(self._bufsize, dtype=np.float)
        self.y4 = np.zeros(self._bufsize, dtype=np.float)
        self.y5 = np.zeros(self._bufsize, dtype=np.float)
        self.y6 = np.zeros(self._bufsize, dtype=np.float)
        self.y7 = np.zeros(self._bufsize, dtype=np.float)
        self.y8 = np.zeros(self._bufsize, dtype=np.float)
        self.y9 = np.zeros(self._bufsize, dtype=np.float)
        self.y10 = np.zeros(self._bufsize, dtype=np.float)
        #self.y2 = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'Voltage Magnitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.plt.setXRange(0,10)
        self.plt.setYRange(.92, 1.07)
        self.curve1 = self.plt.plot(self.x, self.y1, pen=(255, 0, 0))
        self.curve2 = self.plt.plot(self.x, self.y2, pen=(0, 255, 0))
        self.curve3 = self.plt.plot(self.x, self.y3, pen=(255, 0, 255))
        self.curve4 = self.plt.plot(self.x, self.y4, pen=(255, 255, 0))
        self.curve5 = self.plt.plot(self.x, self.y5, pen=(255, 100, 100))
        self.curve6 = self.plt.plot(self.x, self.y6, pen=(20, 150, 0))
        self.curve7 = self.plt.plot(self.x, self.y7, pen=(255, 200, 200))
        self.curve8 = self.plt.plot(self.x, self.y8, pen=(0, 100, 74))
        self.curve9 = self.plt.plot(self.x, self.y9, pen=(25, 40, 180))
        self.curve10 = self.plt.plot(self.x, self.y10, pen=(200, 75, 100))

        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)
        lock = threading.Lock()
        self.lock = lock


        self.app.processEvents()
        count = 0
        self.count = count


    def getdata(self):


        #val = structRet.dataList.returnLastAcq()
        self.lock.acquire()
        val = dataStruct1.returnLastAcq()
        self.lock.release()
        #print("val list",val)
        yList = []
        if (len(dataStruct1.dataValues) > 0):
            for i in range(0,10):
                yList.append(val[i])
            #y2 = np.sin(val[13])
            #print"Y Value = %s" %y1
            #print"Y Value = %s" %y2
            #print("dist list",yList)
            return yList

    def updateplot(self):
        if (len(dataStruct1.dataValues) > 0):
            datagroup = self.getdata()
            self.databuffer1.append(datagroup[0])
            self.databuffer2.append(datagroup[1])
            self.databuffer3.append(datagroup[2])
            self.databuffer4.append(datagroup[3])
            self.databuffer5.append(datagroup[4])
            self.databuffer6.append(datagroup[5])
            self.databuffer7.append(datagroup[6])
            self.databuffer8.append(datagroup[7])
            self.databuffer9.append(datagroup[8])
            self.databuffer10.append(datagroup[9])
            self.y1[:] = self.databuffer1
            self.y2[:] = self.databuffer2
            self.y3[:] = self.databuffer3
            self.y4[:] = self.databuffer4
            self.y5[:] = self.databuffer5
            self.y6[:] = self.databuffer6
            self.y7[:] = self.databuffer7
            self.y8[:] = self.databuffer8
            self.y9[:] = self.databuffer9
            self.y10[:] = self.databuffer10
            #self.y2[:] = self.databuffer2

            # self.sample += 1
            #self.Xwindow += 1
            #self.plt.setXRange(self.sample, self.Xwindow)
            self.curve1.setData(self.x, self.y1)
            self.curve2.setData(self.x, self.y2)
            self.curve3.setData(self.x, self.y3)
            self.curve4.setData(self.x, self.y4)
            self.curve5.setData(self.x, self.y5)
            self.curve6.setData(self.x, self.y6)
            self.curve7.setData(self.x, self.y7)
            self.curve8.setData(self.x, self.y8)
            self.curve9.setData(self.x, self.y9)
            self.curve10.setData(self.x, self.y10)


            self.app.processEvents()


    def run(self):
        #while(structSet.isAlive()):
        self.app.exec_()

# class graphThread(threading.Thread):
#
#     def __init__(self, DynamicPlotter):
#         threading.Thread.__init__(self)
#         self.DynamicPlotter = DynamicPlotter
#         #DynamicPlotter.setDaemon(True)
#
#
#     def run(self):
#
#         self.DynamicPlotter.run()
#
#

#if __name__ == '__main__':

#m = DynamicPlotter(sampleinterval=0.0333, timewindow=10)
#graph = graphThread(m)
#graph.start()

m = DynamicPlotter(sampleinterval=0.0333, timewindow=10.)
def example():
    acquire.connectToModelTest('ephasorDataPlotOut','phasor01_IEEE39')
    structSet.start()
    #structRet.start()
    #structSet.join()
    m.run()

