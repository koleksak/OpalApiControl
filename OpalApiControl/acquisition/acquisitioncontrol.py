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
        self.GroupNumber = GroupNumber
        dataValues = []
        self.dataValues = dataValues

    def returnLastAcq(self):
        """Returns the data for the last acquisition set in acqDir by acquisitionThread as well as
            the last index of acqusitions"""
        lastAcq = len(self.dataValues)
        if(lastAcq == 0):
            return 0
        else:
            data = self.dataValues[lastAcq-1]

            return data

    def showAcquisitionSignals(self,index):
        """Returns a List of the acquisition signals in for the signal group
        as well as the dynamic signals added to the acquisition group. Can only be called
        while model is running"""

        count = 1
        for item in self.dataValues[index]:
            print"Acq ID: {}  Value: {}".format(count,item)
            count +=1

        allSignals = list(OpalApiPy.GetSignalsDescription())
        acqSigsTotal = OpalApiPy.GetNumSignalsForGroup(self.GroupNumber-1)
        acqSignalList = []
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


class StartAcquisitionThread(threading.Thread, DataList):
    def __init__(self, project, model, dataList, GroupNumber, threadName, interval, acq_wait, condition):
        threading.Thread.__init__(self)
        self.project = project
        self.model = model
        self.threadName = str(threadName)
        self.GroupNumber = GroupNumber
        self.interval = interval
        lock = threading.Lock()
        self.lock = lock
        #acq_wait = threading.Event()
        self.acq_wait = threading.Event()
        acq_wait.set()
        self.kill = threading.Event()
        self.condition = condition
        self.dataList = dataList
        simulationTime = 0
        self.simulationTime = simulationTime
        missedData = 0
        self.missedData = missedData
        sampleSec = 0
        self.sampleSec = sampleSec
        monitorInfo = 0
        self.monitorInfo = monitorInfo
        lastAcqTime = 0
        self.lastAcqTime = lastAcqTime
        sample_time_error = 2 * self.interval
        self.sample_time_error = sample_time_error

    def run(self):
        print "Thread- " + self.threadName
        self.lock.acquire()
        try:
            acquire.connectToModel(self.project, self.model)
            modelState, realTimeFactor = OpalApiPy.GetModelState()
            self.lock.release()
        except:
            print 'Could not connect thread ' + self.threadName
        else:
            while(modelState == OpalApiPy.MODEL_RUNNING and self.kill.is_set() is False):#or modelState == OpalApiPy.MODEL_PAUSED):
                if modelState == OpalApiPy.MODEL_PAUSED and self.acq_wait.is_set() is False:
                        #self.acq_wait.clear()
                        #OpalApiPy.Disconnect()
                        logging.warning('Thread Acq {} Paused '.format(self.threadName))
                        self.acq_wait.wait(1)
                        self.acq_wait.set()
                        logging.warning('Thread Acq {} Resumed '.format(self.threadName))
                else:
                    try:
                        self.lock.acquire()
                        acqList = OpalApiPy.GetAcqGroupSyncSignals(self.GroupNumber - 1, 0, 0, 1, 1)
                        self.lock.release()
                    except:
                        logging.warning('<Acquisition Not Available>')
                        break

                sigVals, monitorInfo, simTimeStep, endFrame = acqList
                missedData, offset, self.simulationTime, self.sampleSec = monitorInfo
                if(self.interval <= self.simulationTime-self.lastAcqTime):
                    if (self.sample_time_error <= self.simulationTime - self.lastAcqTime):
                        logging.warning('<Acquisition sample step missed at {}>'.format(self.simulationTime))
                        self.lastAcqTime = self.simulationTime
                    else:
                        # self.lock.acquire()
                        self.condition.acquire()
                        self.dataList.dataValues.append(tuple(sigVals))
                        self.condition.notifyAll()
                        self.condition.release()
                        # self.lock.release()
                        self.lastAcqTime = self.simulationTime
                modelState, realTimeFactor = OpalApiPy.GetModelState()
        self.kill.set()
            #OpalApiPy.Disconnect()
        print "Thread- " + self.threadName + " Exited"


class acquisitionThreadReturn(threading.Thread):
    def __init__(self, project, model, datalist, GroupNumber, threadName, interval, acq_wait, condition, kill):
        threading.Thread.__init__(self)
        self.project = project
        self.model = model
        self.threadName = threadName
        self.GroupNumber = GroupNumber
        self.interval = interval
        self.dataList = datalist
        lock = threading.Lock()
        self.lock = lock
        self.acq_wait = threading.Event()
        acq_wait.set()
        self.kill = threading.Event()
        kill.set()
        self.condition = condition
        new_data = False
        self.new_data = new_data
        lastAcq = 0
        self.lastAcq = lastAcq
        stale_data = 0
        self.stale_data = stale_data

    def run(self):
        print "Thread- " + self.threadName
        self.lock.acquire()
        try:
            acquire.connectToModel(self.project, self.model)
            modelState, realTimeFactor = OpalApiPy.GetModelState()
            self.lock.release()
        except:
            print 'Could not connect thread ' + self.threadName
        else:
            lastIndex = 1
            # while(modelState == OpalApiPy.MODEL_RUNNING):#or modelState == OpalApiPy.MODEL_PAUSED):
            while self.kill.is_set() is False:
                lastEntry = len(self.dataList.dataValues)
                # if((lastEntry != lastIndex) & (len(self.dataList.dataValues) != 0)):
                if modelState == OpalApiPy.MODEL_PAUSED and self.acq_wait.is_set() is False:
                    # self.acq_wait.clear()
                    logging.warning('Thread Acq {} Paused '.format(self.threadName))
                    self.acq_wait.wait(1)
                    self.acq_wait.set()
                    logging.warning('Thread Acq {} Resumed '.format(self.threadName))
                    # break
                if lastEntry != 0:
                    # self.lock.acquire()
                    self.condition.acquire()
                    self.lastAcq = self.dataList.dataValues[lastIndex-1]
                    self.new_data = True
                    self.condition.wait()
                    self.condition.release()
                    lastIndex = lastEntry
                    # self.lock.release()

                # modelState, realTimeFactor = OpalApiPy.GetModelState()

        #OpalApiPy.Disconnect()
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

        #OpalApiPy.Disconnect()
        print"Thread- " + self.threadName + " Exited"


"""*********Below may be useful for keeping track of model time seperate from acquisition threads***********"""


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


def syncAcqReturnInfo(GroupNumber,interval):   ## Useful tool for wholistic information for acquisition group
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
            for items in monitorInfo:
                print("missed Data:{}  offset:{}  simTime:{}  sampleSec:{}".format(missedData, offset, simTime,
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
