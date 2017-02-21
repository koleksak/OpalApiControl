#***************************************************************************************
#Description
# Access Simulink signal control for changing values in Real-Time
# Model must be compiled and connected before signal control is granted
#***************************************************************************************



#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.config import *
# import OpalApiControl.system
# from OpalApiControl.system import acquire
import collections
#***************************************************************************************
# Globals
#***************************************************************************************


#***************************************************************************************
# Main
#*******


def showControlSignals():
    """Displays available subSystems along with their ID and value.
    Read-Write Control Signals
    # Returns a Dictionary of key-value (ID,VALUE) for each signal"""
    subSystemSignals = OpalApiPy.GetControlSignalsDescription()
    systemList = [subSystemSignals]

    print("****************Available Signals******************")
    sigcount = 1
    iDList = []
    for systems in systemList:
        sigcount =+1
        systemInfo = systems
        for signal in systemInfo:
            signalType, subSystemId, path, signalName, reserved, readonly, value = signal
            iDList.append(subSystemId)
            print("SubSystem Name:{}  SubSystemID:{}  SignalName:{}  Value:{}".format(path, subSystemId, signalName, value))



def getControlSignalsDict():
    """"# Returns a Dictionary of key-value (ID,VALUE) for each control signal. Model must be loaded
    Read-Write Control Signals"""

    iDList = []
    num = 1
    signalDict = dict.fromkeys(iDList)
    for item in list(OpalApiPy.GetControlSignals(1)):
        signalDict[num] = item
        num += 1

    return signalDict

def numControlSignals():
    """Returns number of controllable signals in model.Model must be loaded"""
    count = 0
    for num in OpalApiPy.GetControlSignals(1):
        count +=1

    return count


def showSignals():
    """Displays a list of signals(non-control signals) by Name, ID and Value
    Read-Only Dynamic Signals"""

    allSignals = list(OpalApiPy.GetSignalsDescription())
    # print("signal list before cut: ", allSignals)

    #Remove control signals from list
    numControl = numControlSignals()
    del allSignals[:numControl]

    dynSignalList = []
    for signalList in allSignals:
        signal = [signalList]
        for spec in signal:
            signalType, signalId, path, signalName, reserved, readonly, value = spec
            if(signalType == 1):
                dynSignalList.append(signal)
                print("Signal Name:{} SignalID:{} Value:{}".format(path, signalId, value))

def getSignalsDict():
    """Returns a dictionary of key-value(ID,VALUE) for signals(NOT control signals)
    Read-Only Dynamic Signals"""
    allSignals = list(OpalApiPy.GetSignalsDescription())
    # print("signal list before cut: ", allSignals)

    # Remove control signals from list
    numControl = numControlSignals()
    del allSignals[:numControl]

    dynValueList = []
    for signalList in allSignals:
        signal = [signalList]
        for spec in signal:
            signalType, signalId, path, signalName, reserved, readonly, value = spec
            if (signalType == 1):

                dynValueList.append(value)

    iDList = []
    num = 1
    signalDict = dict.fromkeys(iDList)
    for item in list(dynValueList):
        signalDict[numControl+num] = item                  # start at ID, but can start at 1 if needed.
        num += 1

    return signalDict



def accessAllSignals():    ######Might not be needed since set signal overrides signalControl
    """"Gives user access to models's control signals. One client API granted signal control at a time"""

    subsystemId = 0     # 0 takes control of all subsystems
    signalControl = 0   # requests signal control when value == 1

    # Connect to model if connection is not already made
    acquire.connectToModel()
    modelState,realTimeMode = OpalApiPy.GetModelState()

    try:
        if(modelState == OpalApiPy.MODEL_RUNNING):
            # Access signal control
            signalControl = 1
            OpalApiPy.GetSignalControl(subsystemId,signalControl)
            print "Signal control accessed"
        else:
            print "Model state not ready for signal access"
    finally:
        print "Release signal control after changing values"

def releaseAllSignals():
    """Releases all signal controls"""
    OpalApiPy.GetSignalControl(0,0)
    print "All signal controls released"

def releaseSignal():  #### Might not be needed
    """Release subsystem by subsystem Id (one value at a time for now)"""
    subSystemList = OpalApiPy.GetSubsystemList()
    for subSystemInfo in subSystemList:
        print ("Subsystems:", subSystemInfo)
        subSystemName, subSystemId, nodeName = subSystemInfo
        print ("Subsystem Name:{}   Subsystem ID:{}    NodeName:{}".format(subSystemName, subSystemId, nodeName))
    chooseId = (int(raw_input("Choose subsystem Id to be released: ")))
    OpalApiPy.GetSignalControl(int(chooseId),0)
    print "Subsystem %s control released." % chooseId

def accessSignal():   ######Might not be needed. setSignal accesses signal control
    """Access subsystem by subsystem Id (one value at a time for now)"""
    acquire.connectToModel()
    subSystemList = OpalApiPy.GetSubsystemList()

    # Displays available subSystems along with their ID and value.
    subSystemSignals = OpalApiPy.GetControlSignalsDescription()
    systemList = [subSystemSignals]

    print("****************Available Signals******************")
    for systems in systemList:
        systemInfo = systems
        for signal in systemInfo:

            signalType, subSystemId, path, signalName, reserved, readonly, value = signal
            print("SubSystem Name:{}  SubSystemID:{}  SignalName:{}  Value:{}".format(path,subSystemId,signalName,value))


    chooseId = (int(raw_input("Choose subsystem Id to be accessed: ")))
    OpalApiPy.GetSignalControl(chooseId, 1)

    print "Subsystem %s control accessed." %chooseId


    signalType, subSystemId, path, label, reserved, readonly, value = subSystemSignals[chooseId-1]
    print("Subsystem Name:{}  Signal Name:{} SignalID:{}  ReadOnly:{} Value:{}".format(path,label,chooseId,readonly,value))


# def setControlSignal(signalId,newSignalValue):    ###REMOVE???
#     """Change signal values by signal subsystem ID,
#      newSignal values takes tuple of values mapped to each signal of the chosen subsystem
#      in consecutive order as specified by the sc_user_interface list"""
#     controlChange = 1
#
#     # accessSignal()
#     # OpalApiPy.SetSignalsByName(signalNames,newSignalValues)   ###REMOVE
#     print" SignalID:%s" %signalId
#     controlSignalValues = list(OpalApiPy.GetControlSignals(1))
#     print"Control Sig Values:%s" %controlSignalValues
#     controlSignalValues[signalId-1] = newSignalValue
#
#     OpalApiPy.SetSignalsById(signalId,tuple(controlSignalValues))
#     print("Signal:{} New Signal Value:{}".format(signalId,newSignalValue))
#
#     #Release Signal Controls
#     controlChange = 0
#     OpalApiPy.GetSignalControl(controlChange,signalId)
#






# def setSignals():               ##CANT SET THESE!!! ADD ARGUMENTS ###NOT NEEDED,CAN USE TO RETURN OTHER SIGNAL VALUES (NONCONTROL SIGNALS)
#     """
#     """
#
#
#
#     signalInfo = OpalApiPy.GetSignalsDescription()
#
#     for signalList in signalInfo:
#         signal = [signalList]
#         for spec in signal:
#             signalType,signalId,path,signalName,reserved,readonly,value = spec
#             print("Signal Name:{} SignalID:{} Value:{}".format(path,signalId,value))
#
#     OpalApiPy.GetSignalControl(1,0)
#     controlSignalValues = OpalApiPy.GetControlSignals(1)
#
#     OpalApiPy.SetSignalsById((1,4),(300,100))
#     print("**************Values Changed****************")
#
#     for signalList in signalInfo:
#         signal = [signalList]
#         for spec in signal:
#             signalType,signalId,path,signalName,reserved,readonly,value = spec
#             print("Signal Name:{} SignalID:{} Value:{}".format(path,signalId,value))


def setControlSignals(signalIDS,newSignalValues):
    """Change signal values by signal subsystem names
        signalNames can by a tuple (name1,name2....,nameN) or a single name
        newSignalValues can also by a tuple (newValue1,newValue2,....newValueN), or a single value.
        Item indexes in the signal tuple correspond to respective numeric values in the value tuple """
    # controlChange = 1
    # signalID = 1

    OpalApiPy.SetSignalsById(signalIDS,newSignalValues)

    # controlSignalValues = list(OpalApiPy.GetControlSignals(1))  ###REMOVE???
    # newSignalValues = list(newSignalValues)
    #
    # # print"signalChange: %s" %signalChange
    # print"newsignalvalues %s" %newSignalValues
    # num = 0
    # for newVals in signalIDS:
    #     controlSignalValues[newVals-1] = newSignalValues[num]
    #     num+=1
    #
    # newSignalValuesList = tuple(controlSignalValues)
    # print("SignalChange: " , controlSignalValues)
    #
    # OpalApiPy.SetControlSignals(controlChange, newSignalValuesList)
    # print("Signal:{} New Signal Value:{}".format(signalIDS, newSignalValues))

    #Release All Control Signals
    # controlChange = 0
    # OpalApiPy.GetSignalControl(controlChange, 0)
