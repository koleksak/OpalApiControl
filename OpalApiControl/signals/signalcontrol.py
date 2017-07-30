#***************************************************************************************
#Description
# Access Simulink signal control signals for reading and/or changing values in Real-Time
# Model must be compiled and connected before signal control is granted
#***************************************************************************************


#***************************************************************************************
# Modules
#***************************************************************************************

from OpalApiControl.system import acquire
import OpalApiPy
import collections
#***************************************************************************************
# Globals
#***************************************************************************************


#***************************************************************************************
# Main
#*******


def showControlSignals():
    """Displays available subSystems along with their ID and value.
    Read-Write Control Signals"""
    #OpalApiPy.GetSignalControl(0, 1)
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
    #OpalApiPy.GetSignalControl(0, 0)


def getControlSignalsDict():   #NEW FUNCTION IN PROGRES, ORDERED DICT for ID, key-name, value-value
    """"# Returns a Dictionary of key-value (ID,VALUE) for each control signal. Model must be loaded
    Read-Write Control Signals.  ID, Value pairs are ordered by model specification in the OpCommBlock"""

    iDList = []
    num = 1
    signalDict = dict.fromkeys(iDList)
    for item in list(OpalApiPy.GetControlSignals(1)):
        signalDict[num] = item
        num += 1
    subSystemSignals = OpalApiPy.GetControlSignalsDescription()
    systemList = [subSystemSignals]

    iDList = []
    ControlSignals = {}
    for systems in systemList:
        systemInfo = systems
        for signal in systemInfo:
            signalType, subSystemId, path, signalName, reserved, readonly, value = signal
            ControlSignals[signalName] = value
            #print("SubSystem Name:{}  SubSystemID:{}  SignalName:{}  Value:{}".format(path, subSystemId, signalName, value))

    return ControlSignals


def numControlSignals():
    """Returns number of controllable signals in model.Model must be loaded"""
    count = 0
    for num in OpalApiPy.GetControlSignals(1):
        count +=1

    return count


def showSignals():
    """Displays a list of signals(non-control signals) by Name, ID and Value
    Read-Only Dynamic Signals. """

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

def acquisitionSignalsParse(project, model):
    """Parses acquisition signals from main signal description list. Designed for use with setting
    IdxVgs and Varheader in ePhasorsim acquisition port selection"""
    acquire.connectToModel(project, model)
    allSignals = list(OpalApiPy.GetSignalsDescription())
    ephasor_port_out = []
    for signal in allSignals:
        if signal[0] == 0:
            ephasor_port_out.append(signal[3])
    OpalApiPy.Disconnect()
    return ephasor_port_out


def setControlSignals(signalIDS, newSignalValues):
    """Change signal values by signal subsystem names
        signalNames can be a tuple (name1,name2....,nameN) or a single name
        newSignalValues can also by a tuple (newValue1,newValue2,....newValueN), or a single value.
        Item indexes in the signal tuple correspond to respective numeric values in the value tuple """
    # controlChange = 1
    # signalID = 1

    #This is the OPAL API function call for setting signals. It is strictly called in this method, to allow
    #for further expansion of setting the control signals for future updates, or through the
    #set control signals call itself. It differs from other functions in the API interface modules
    #as it doesn't take tuple (ID,Value) pairs, but is the quickest set function.
    OpalApiPy.SetSignalsById(signalIDS, newSignalValues)

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



#  The functions below were implemented to deal with access rights when calling for signal information
# and changing signals.  It appears that setting signals itself, gives user access to the signal control
# but the functions have been kept for future expansion if multiple user collisions ever start occurring.
# This may be a means for solving access issues if two different systems are used to change signal values
# for testing purposes
#***Access All Signals, Release All signals are not strictly defined yet.***

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
