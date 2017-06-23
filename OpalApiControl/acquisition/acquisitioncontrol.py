#***************************************************************************************
#Description
#Module for creating data lists and acquisition threads to store data and
#retrieve data from running RT-Lab model. Threads for setting data and retrieving data available.
#
#
#***************************************************************************************



#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.system import acquire
import os
import OpalApiPy
import threading
import multiprocessing
from time import sleep
import logging



#***************************************************************************************
# Globals
#***************************************************************************************



#***************************************************************************************
# Main
#*******

"""!!!!MAKE SHOW ACQUISITION DATA FUNCTION OUTSIDE OF OBJECT(MODEL MUST BE RUNNING)!!!!"""

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
        if(lastAcq == 0):
            return 0
        # print"Last Acquisition for Group %i" %self.GroupNumber
        #if(lastAcq != 0):
        # print(self.dataValues[lastAcq-1])
        else:
            return self.dataValues[lastAcq-1]
        #else:
        #    print"NO Data available"

    def showAcquisitionSignals(self,index):
        """Returns a List of the acquisition signals in for the signal group
        as well as the dynamic signals added to the acquisition group"""
        count = 1
        for item in self.dataValues[index]:
            print"Acq ID: {}  Value: {}".format(count,item)
            count +=1

        allSignals = list(OpalApiPy.GetSignalsDescription())
        # print("signal list before cut: ", allSignals)
        acqSigsTotal = OpalApiPy.GetNumSignalsForGroup(self.GroupNumber-1)
        acqSignalList = []
        dynSignalList = []
        print"*****Acquisition Signals*****"
        acqCount = 0
        for signalList in allSignals:
            signal = [signalList]
            for spec in signal:
                signalType, signalId, path, signalName, reserved, readonly, value = spec
                if (signalType == 0):
                    acqSignalList.append(signal)
                    print("Acq Signal #: {}  Signal Name:{} SignalID:{} Value:{}".format(acqCount+1,path, signalId, value))
                    acqCount += 1

        # These are any of the dynamic signals added to the acquisition group that
        # were not specified in the OpComm block as received signals in sm_console
        if(acqSigsTotal > acqCount):
            print"*****Additional Dynamic Signals In Group*****"
            dynSig = acqCount
            for item in range(acqCount,acqSigsTotal):
                print"Acq Signal #: {}  Value: {} ".format(dynSig + 1,self.dataValues[index][dynSig])
                dynSig +=1


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
        self.monitorInfo = monitorInfo
        lastAcq = 0
        self.lastAcq = lastAcq


    def run(self):
        print "Thread- " + self.threadName
        # project = 'ephasorex2'
        # model = 'phasor1_IEEE39'
        acquire.connectToModel(self.project,self.model)
        modelState,realTimeFactor = OpalApiPy.GetModelState()
        while(modelState == OpalApiPy.MODEL_RUNNING and modelState != OpalApiPy.MODEL_PAUSED):


            # print"Lock acquired by %s" %self.threadName
            try:
                acqList = OpalApiPy.GetAcqGroupSyncSignals(self.GroupNumber - 1, 0, 0, 1, 1)

            except:
               logging.warning('Thread Acq {} Exited '.format(self.threadName))
               break

            sigVals, monitorInfo, simTimeStep, endFrame = acqList
            missedData,offset,self.simulationTime,self.sampleSec = monitorInfo
            if(self.simulationTime-self.lastAcq >= self.interval):
                self.lock.acquire()
                self.dataList.dataValues.append(tuple(sigVals))
                #print sigVals
                self.lock.release()
                self.lastAcq = self.simulationTime
                #print("simTime at Acq: ", self.simulationTime)
                #print("sampleSec: ", self.sampleSec)
            else:
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                continue
                #print("simTime Last Acq: ", self.simulationTime)
            # dataList = DataList(self.GroupNumber)
            #self.dataList.dataValues.append(tuple(sigVals))
            # print"Lock Released by %s" %self.threadName

            modelState, realTimeFactor = OpalApiPy.GetModelState()
             #print"Last Acq Time is %s" %simulationTime
            # sleep(self.interval)

        OpalApiPy.Disconnect()
        #print"Thread- " + self.threadName + " Exited"




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
        lastAcq = 0
        self.lastAcq = lastAcq

    def run(self):
        print "Thread- " + self.threadName
        acquire.connectToModel(str(self.project), str(self.model))
        modelState, realTimeFactor = OpalApiPy.GetModelState()
        lastIndex = 1
        while(modelState == OpalApiPy.MODEL_RUNNING):
            lastEntry = len(self.dataList.dataValues)
            modelState, realTimeFactor = OpalApiPy.GetModelState()
            if((lastEntry != lastIndex) & (len(self.dataList.dataValues) != 0)):
                self.lock.acquire()
                # print"Lock Acquired by %s" %self.threadName
                # print("Last acquisition call returns- {}".format(self.dataList.dataValues[lastIndex-1]))
                self.lastAcq = self.dataList.dataValues[lastIndex-1]
                lastIndex = lastEntry
                # print"Lock Released by %s" %self.threadName
                self.lock.release()
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                # sleep(self.interval)

        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"


class StartAcquisitionThreadWithTime(threading.Thread,DataList):    #REMOVE
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
        clockTime = simulationTimeThread(self.project,self.model,self.interval)
        # clockTime.setDaemon(True)
        clockTime.start()
        clockTime.join(1)
        simulationClock = clockTime.simulationClock
        previousAcqClock = 0
        while(modelState == OpalApiPy.MODEL_RUNNING):
            if (self.interval < (simulationClock - previousAcqClock)):
                #print"simclock %s" % simulationClock
                #print"prev acq clock %s" % previousAcqClock
                self.lock.acquire()
                #print"Lock acquired by %s" %self.threadName
                acqList = OpalApiPy.GetAcqGroupSyncSignals(self.GroupNumber - 1, 0, 0, 1, self.interval)
                sigVals, monitorInfo, simTimeStep, endFrame = acqList
                # dataList = DataList(self.GroupNumber)
                self.dataList.dataValues.append(tuple(sigVals))
                #print"Lock Released by %s" %self.threadName
                self.lock.release()
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                previousAcqClock = simulationClock
                #print"Thread Sleeping"
                #sleep(self.interval)
                #print"Thread UP"

            else:
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                simulationClock = clockTime.simulationClock

        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"


class acquisitionThreadReturnWithTime(threading.Thread):         #REMOVE
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
        lastAcq = []
        self.lastAcq = lastAcq
        simulationClock = 0
        self.simulationClock = simulationClock
        # self.setDaemon(True)

    def run(self):
        print "Thread- " + self.threadName
        acquire.connectToModel(str(self.project), str(self.model))
        modelState, realTimeFactor = OpalApiPy.GetModelState()
        clockTime = simulationTimeThread(self.project, self.model,self.interval)
        #SetDaemon makes sure simulationTimeThread is killed when its calling thread finishes
        clockTime.setDaemon(True)
        clockTime.start()
        #Joins to its calling thread and the main thread
        clockTime.join(2)
        #self.simulationClock = clockTime.simulationClock
        previousAcqClock = 0
        lastIndex = 1
        while(modelState == OpalApiPy.MODEL_RUNNING):
            lastEntry = len(self.dataList.dataValues)
            # Retrieves last acquisition signals if the specified interval is exceeded
            if (self.interval < (self.simulationClock - previousAcqClock)):
                #Must update the model state consecutively to know when state has changed
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                if((lastEntry != lastIndex) & (len(self.dataList.dataValues) != 0)):
                    self.lock.acquire()
                    # print"Lock Acquired by %s" %self.threadName
                    # print("Last acquisition call returns- {}".format(self.dataList.dataValues[lastIndex-1]))
                    self.lastAcq = self.dataList.dataValues[lastIndex - 1]
                    #print("Last Acq: ",self.lastAcq)
                    #print("simulation clock",simulationClock)
                    lastIndex = lastEntry
                    # print"Lock Released by %s" %self.threadName
                    self.lock.release()
                    modelState, realTimeFactor = OpalApiPy.GetModelState()
                    previousAcqClock = self.simulationClock
                    # sleep(self.interval)
            else:

                #Updates clocktime until interval is exceeded
                modelState, realTimeFactor = OpalApiPy.GetModelState()
                self.simulationClock = clockTime.simulationClock


        #Thread must disconnect from the model when finished.
        OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"


# acqDir = []
# acqList = 0
###CAN POSSIBLY REMOVE BELOW
class simulationTimeThread(threading.Thread):
    # Use of the simulation time thread requires that calls for time differences are equal to
    # or greater than the simulation sample/sec as specified in the model's OpComm Block.
    # This thread is used to compare time differences at a specified interval when a simulation clock
    # is added to the main model in RT-Lab. Primary use of this function is in the
    # acquisitionThreadReturnWithTime object thread, for setting acquisition return intervals

    def __init__(self,project,model,interval):
        """Interval must be greater or equal to model simulation sample/sec"""
        threading.Thread.__init__(self)
        self.project = str(project)
        self.model = str(model)
        self.interval = interval
        threadName = 'SimulationClock Thread'
        self.threadName = threadName
        lock = threading.Lock()
        projectPath = 0
        modelName = 0
        self.projectPath = projectPath
        self.modelName = modelName
        self.lock = lock

        simulationClock = 0
        self.simulationClock = simulationClock

    def run(self):
        #Each thread must connect itself to the model through the acquire module
        acquire.connectToModel(self.project, self.model)
        self.projectPath, self.modelName = OpalApiPy.GetCurrentModel()
        modelName = os.path.splitext(self.modelName)

        #This is the default clock path as long as the user adds a clock to the sm_master for
        #time keeping if asynchronous data acquisition is needed.
        clockpath = modelName[0] + '/sm_master/clock/port1'
        modelState, realTimeFactor = OpalApiPy.GetModelState()
        while (modelState == OpalApiPy.MODEL_RUNNING):
            # Thread continues to get time until model is paused or stoped
            #Blocks GetSignalsByName process from other threads until time thread is done
            self.lock.acquire()
            self.simulationClock = OpalApiPy.GetSignalsByName(clockpath)
            # print"Simulation Time is %s" % self.simulationClock
            self.lock.release()
            modelState, realTimeFactor = OpalApiPy.GetModelState()
            sleep(self.interval)

        #Each thread must also disconnect from the API after its work has finished.
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


def syncAcqReturn(GroupNumber,interval):   ## This has been replaced by acquisitionThreadWIthTime object
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


#Multiprocessing routines require knowledge of pickling data from process to process

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
