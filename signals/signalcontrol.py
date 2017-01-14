#***************************************************************************************
#Description
# Access Simulink signal control for changing values in Real-Time
# Model must be compiled and connected before signal control is granted
#***************************************************************************************



#***************************************************************************************
# Modules
#***************************************************************************************
from OpalApiControl.config import *
import OpalApiControl.system
from OpalApiControl.system import acquire





#***************************************************************************************
# Globals
#***************************************************************************************








#***************************************************************************************
# Main
#*******



def signalAccess():
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

def signalReleaseAll():
    """Releases all signal controls"""
    OpalApiPy.GetSignalControl(0,0)
    print "All signal controls released"

def releaseSubSystem():
    """Release subsystem by subsystem Id (one value at a time for now)"""
    subSystemList = OpalApiPy.GetSubsystemList()
    for subSystemInfo in subSystemList:
        print ("Subsystems:", subSystemInfo)
        subSystemName, subSystemId, nodeName = subSystemInfo
        print ("Subsystem Name: {}   Subsystem ID: {}    NodeName: {}".format(subSystemName, subSystemId, nodeName))
    chooseReleaseId = raw_input("Choose subsystem Id to be released: ")
    OpalApiPy.GetSignalControl(int(chooseReleaseId),0)
    print "Subsystem %s control released." % subSystemId

def accessSubSystem():
    """Access subsystem by subsystem Id (one value at a time for now)"""
    subSystemList = OpalApiPy.GetSubsystemList()
    for subSystemInfo in subSystemList:
        print ("Subsystems:", subSystemInfo)
        subSystemName, subSystemId, nodeName = subSystemInfo
        print ("Subsystem Name: {}   Subsystem ID: {}    NodeName: {}".format(subSystemName,subSystemId,nodeName))
    chooseReleaseId = raw_input("Choose subsystem Id to be accessed: ")
    OpalApiPy.GetSignalControl(int(chooseReleaseId), 1)
    print "Subsystem %s control accessed." % subSystemId
