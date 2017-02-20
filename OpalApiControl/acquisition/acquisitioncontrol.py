#***************************************************************************************
#Description
#Module for creating data lists and acquisition threads to store data and
#retrieve data from running RT-Lab model.
#
#***************************************************************************************



#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.config import *
import threading
import multiprocessing
from time import sleep



#***************************************************************************************
# Globals
#***************************************************************************************



#***************************************************************************************
# Main
#*******


class DataList:
    # Creates a data structure for an acquisition group thread
    def __init__(self,GroupNumber):
        # self.listName = listName
        self.GroupNumber = GroupNumber
        dataValues = []
        self.dataValues = dataValues
        #simulationTime = 0
        #self.simulationTime = simulationTime

    def returnLastAcq(self):
        """Returns the data for the last acquisition set in acqDir by acquisitionThread as well as
            the last index of acqusitions"""
        lastAcq = len(self.dataValues)
        print"Last Acquisition for Group %i" %self.GroupNumber
        print(self.dataValues[lastAcq-1])

    def showAcquisitionSignals(self,index):
        """Returns a List of the acquisition signals in for the signal group
        as well as the dynamic signals added to the acquisition group"""
        count = 1
        for item in self.dataValues[index]:
            print"Acq ID: {}  Value: {}".format(count,item)
            count +=1






# acqDir = []
# acqList = 0
class simulationTimeThread(threading.Thread):   # Work in Progress for accessing simulation clock
    def __init__(self,project,model,interval):
        """Interval must be greater or equal to model simulation sample/sec"""
        threading.Thread.__init__(self)
        self.project = str(project)
        self.model = str(model)
        self.interval = interval
        threadName = 'SimulationClock Thread'
        self.threadName = threadName
        lock = threading.Lock()
        self.lock = lock

        simulationClock = 0
        self.simulationClock = simulationClock

    def run(self):
        acquire.connectToModel(self.project, self.model)
        projectPath, modelName = OpalApiPy.GetCurrentModel()
        modelName = os.path.splitext(modelName)
        clockpath = modelName[0] + '/sm_master/clock/port1'
        modelState, realTimeFactor = OpalApiPy.GetModelState()
        while (modelState == OpalApiPy.MODEL_RUNNING):
            self.lock.acquire()
            self.simulationClock = OpalApiPy.GetSignalsByName(clockpath)
            print"Simulation Time is %s" % self.simulationClock
            self.lock.release()
            modelState, realTimeFactor = OpalApiPy.GetModelState()
            sleep(self.interval)



        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"



class StartAcquisitionThread(threading.Thread,DataList):
    def __init__(self,project,model,dataList,GroupNumber,threadName,interval):
        threading.Thread.__init__(self)
        self.project = project
        self.model = model
        self.threadName = str(threadName)
        self.GroupNumber = GroupNumber
        self.interval = interval
        lock = threading.Lock()
        self.lock = lock
        self.dataList = dataList
        simulationTime = 0
        self.simulationTime = simulationTime
        missedData = 0
        self.missedData = missedData
        sampleSec = 0
        self.sampleSec = sampleSec
        monitorInfo = 0
        self.monitorInfor = monitorInfo


    def run(self):
        print "Thread- " + self.threadName
        # project = 'ephasorex2'
        # model = 'phasor1_IEEE39'
        acquire.connectToModel(self.project,self.model)
        modelState,realTimeFactor = OpalApiPy.GetModelState()
        while(modelState == OpalApiPy.MODEL_RUNNING):

            self.lock.acquire()
            print"Lock acquired by %s" %self.threadName
            acqList = OpalApiPy.GetAcqGroupSyncSignals(self.GroupNumber - 1, 0, 0, 1, self.interval)
            sigVals, monitorInfo, simTimeStep, endFrame = acqList
            missedData,offset,simulationTime,sampleSec = monitorInfo
            # dataList = DataList(self.GroupNumber)
            self.dataList.dataValues.append(tuple(sigVals))
            modelState,realTimeFactor = OpalApiPy.GetModelState()
            print"Lock Released by %s" %self.threadName
            self.lock.release()
            print"Last Acq Time is %s" %simulationTime
            # sleep(self.interval)

        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"




class acquisitionThreadReturn(threading.Thread):
    def __init__(self,project,model,datalist,GroupNumber,threadName,interval):
        threading.Thread.__init__(self)
        self.project = project
        self.model = model
        self.threadName = threadName
        self.GroupNumber = GroupNumber
        self.interval = interval
        lock = threading.Lock()
        self.dataList = datalist
        self.lock = lock

    def run(self):
        print "Thread- " + self.threadName
        acquire.connectToModel(str(self.project), str(self.model))
        modelState, realTimeFactor = OpalApiPy.GetModelState()
        lastIndex = 0
        while(modelState == OpalApiPy.MODEL_RUNNING):
            lastEntry = len(self.dataList.dataValues)
            if((lastEntry != lastIndex) & (len(self.dataList.dataValues) != 0)):
                self.lock.acquire()
                print"Lock Acquired by %s" %self.threadName
                print("Last acquisition call returns- {}".format(self.dataList.dataValues[lastIndex-1]))
                lastIndex = lastEntry
                print"Lock Released by %s" %self.threadName
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                self.lock.release()
                # sleep(self.interval)

        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"

def returnLastAcq(GroupNumber):   ##Made this a class function ***CAN REMOVE***
    """Returns the data for the last acquisition set in acqDir by acquisitionThread as well as
    the last index of acqusitions"""

    lastAcq = len(DataList.dataValues)
    return lastAcq, DataList.dataValues[lastAcq-1]


class StartAcquisitionThreadWithTime(threading.Thread,DataList):
    def __init__(self,project,model,dataList,GroupNumber,threadName,interval):
        threading.Thread.__init__(self)
        self.project = str(project)
        self.model = str(model)
        self.GroupNumber = GroupNumber
        self.threadName = threadName
        self.interval = interval
        lock = threading.Lock()
        self.lock = lock
        self.dataList = dataList


    def run(self):
        print "Thread- " + self.threadName
        acquire.connectToModel(self.project,self.model)
        modelState,realTimeFactor = OpalApiPy.GetModelState()
        clockTime = simulationTimeThread(self.project,self.model)
        clockTime.start()
        clockTime.join(1)
        simulationClock = clockTime.simulationClock
        previousAcqClock = 0
        while(modelState == OpalApiPy.MODEL_RUNNING):
            if (self.interval < (simulationClock - previousAcqClock)):
                print"simclock %s" % simulationClock
                print"prev acq clock %s" % previousAcqClock
                self.lock.acquire()
                print"Lock acquired by %s" %self.threadName
                acqList = OpalApiPy.GetAcqGroupSyncSignals(self.GroupNumber - 1, 0, 0, 1, 1)
                sigVals, monitorInfo, simTimeStep, endFrame = acqList
                # dataList = DataList(self.GroupNumber)
                self.dataList.dataValues.append(tuple(sigVals))
                modelState,realTimeFactor = OpalApiPy.GetModelState()
                print"Lock Released by %s" %self.threadName
                self.lock.release()
                previousAcqClock = simulationClock
                #print"Thread Sleeping"
                #sleep(self.interval)
                #print"Thread UP"

            else:
                clockTime = simulationTimeThread(self.project,self.model)
                clockTime.start()
                clockTime.join(1)
                simulationClock = clockTime.simulationClock

        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"



def getSyncClockPath(project,model):   #ADDED To acquisition thread class CAN POSSIBLY REMOVE
    """Returns model clock path for asynchronous acquisition"""

    acquire.connectToModel(project,model)
    projectPath, modelName = OpalApiPy.GetCurrentModel()
    modelName = os.path.splitext(modelName)
    clockpath = modelName[0] + '/sm_master/clock/port1'
    simulationTime = OpalApiPy.GetSignalsByName(clockpath)
    return simulationTime


def syncAcqReturn(GroupNumber,interval):
    """Performs data acquisition at the specified time interval if the model is
    running, until the model stops running"""
    #Data Acquisition parameters
    acqGroup = GroupNumber-1
    synchronization = 0
    interpolation = 0
    threshold = 1
    acqTimeStep = 0.001

    dataRequestTime = 0
    acqControl = 1
    acquire.connectToModel('ephasorex2', 'phasor01_IEEE39')
    projectPath,modelName = OpalApiPy.GetCurrentModel()
    modelName = os.path.splitext(modelName)
    clockpath = modelName[0] + '/sm_master/clock/port1'
    simulationClock = OpalApiPy.GetSignalsByName(clockpath)
    previousAcqClock = 0
    print(simulationClock)
    # try:
    modelState,realTimeMode = OpalApiPy.GetModelState()
    print"model state %s" %modelState
    OpalApiPy.GetAcquisitionControl(acqControl, GroupNumber)

    numTriggers = 0
    while(modelState == OpalApiPy.MODEL_RUNNING):
        simulationClock = OpalApiPy.GetSignalsByName(clockpath)
        if(interval < (simulationClock-previousAcqClock)):

            print"simclock %s" %simulationClock
            print"prev acq clock %s" %previousAcqClock
            previousAcqClock = simulationClock

            acqList = OpalApiPy.GetAcqGroupSyncSignals(acqGroup, synchronization, interpolation, \
                                                                             threshold, acqTimeStep)

            sigVals, monitorInfo, simTimeStep, endFrame = acqList
            missedData, offset, simTime, sampleSec = monitorInfo

            # sets async data acquisiion to group #,rearm trigger after S seconds
            repeat = True
            for items in monitorInfo:
                print("missed Data:{}  offset:{}  simTime:{}  sampleSec:{}".format(missedData, offset, simTime, \
                                                                                   sampleSec))
            portID = 1
            for item in sigVals:
                print("ID:{}  Value:{} ".format(portID, item))
                # sampleTimeInterval = OpalApiPy.GetAcqSampleTime(1)
                # print("Sample acq interval", sampleTimeInterval)
                portID += 1

            numTriggers += 1
            print"Acquisition triggered %s times" % numTriggers
            modelState, realTimeMode = OpalApiPy.GetModelState()

        else:
            print"Interval Range not exceeded"
            modelState, realTimeMode = OpalApiPy.GetModelState()
            # previousAcqClock = simulationClock


    if(modelState != OpalApiPy.MODEL_RUNNING):
        print"Model must be running to trigger data acquisition"
        OpalApiPy.GetAcquisitionControl(acqControl, GroupNumber)
        print"Group acquisition control released"

    OpalApiPy.Disconnect()
    # except:
    #     print"Error: acquisition failed"
    #
    # finally:
    #     acqControl = 0
    #     OpalApiPy.GetAcquisitionControl(acqControl,group)
    #     print"Group acquisition control released"


def showAcquisitionSignals(acqGroup):
    """Shows the list of acquisition signals in the specified group"""

class acquisitionMultiProc(multiprocessing.Process):   ###Have not successfully implemented
    def __init__(self,processID,name,counter,GroupNumber,interval):
        multiprocessing.Process.__init__(self)
        self.processID = processID
        self.name = name
        self.counter = counter
        self.GroupNumber = GroupNumber
        self.interval = interval


    def run(self):
        print "Process- " + self.name
        OpalApiPy.GetAcqGroupSyncSignals(0,0,0,1,0.001)
        print"Process- " +self.name + " Exited"
        # self.join()
