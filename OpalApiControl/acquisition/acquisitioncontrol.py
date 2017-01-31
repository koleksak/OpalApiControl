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



def acquisitionReturn(GroupNumber):
    """Access control to acquisition signals.Model Must be Running"""
    modelState,realtimeMode = OpalApiPy.GetModelState()
    print(modelState)

    try:
        if(modelState == OpalApiPy.MODEL_RUNNING):

            acqGroup = GroupNumber
            synchronization = 0
            interpolation = 0
            threshold = 1
            acqTimeStep = 0.001

            while(modelState == OpalApiPy.MODEL_RUNNING):

                acqList = OpalApiPy.GetAcqGroupSyncSignals(acqGroup,synchronization,interpolation, \
                                                           threshold,acqTimeStep)

                sigVals, monitorInfo,simTimeStep,endFrame = acqList

                portID = 1
                for item in sigVals:
                    print("ID:{}  Value:{}".format(portID,item))
                    portID +=1

        else:
            print("Model must be running before data acquisition")

    finally:
        #Release acquisition control
        OpalApiPy.GetAcquisitionControl(0,GroupNumber)
        OpalApiPy.Disconnect()
        print("Disconnected from model")



def showAcquisitionSignals(acqGroup):
    """Shows the list of acquisition signals in the specified group"""