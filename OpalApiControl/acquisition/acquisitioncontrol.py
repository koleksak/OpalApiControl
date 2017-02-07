#***************************************************************************************
#Description
#
#
#***************************************************************************************



#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.config import *





#***************************************************************************************
# Globals
#***************************************************************************************



#***************************************************************************************
# Main
#*******


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

    # except:
    #     print"Error: acquisition failed"
    #
    # finally:
    #     acqControl = 0
    #     OpalApiPy.GetAcquisitionControl(acqControl,group)
    #     print"Group acquisition control released"


def showAcquisitionSignals(acqGroup):
    """Shows the list of acquisition signals in the specified group"""