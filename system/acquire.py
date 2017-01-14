# ***************************************************************************************
# Description
#
# Connect to a running or paused model. If the model is not running, it will be executed.
# Model must be compiled and assigned prior to connecting.
# ***************************************************************************************


# ***************************************************************************************
# Modules
# ***************************************************************************************
from OpalApiControl.config import *

# ***************************************************************************************
# Globals
# ***************************************************************************************
# list of returned model state
modelStateList = ["not connected", "not loadable", "compiling", "loadable", "loading", \
                  "resetting", "loaded", "paused", "running", "disconnected"]

realTimeModeList = {'Hardware Sync':0, 'Simulation':1, 'Software Sync':2, 'Not Used':3, 'Low Priority Sim':4}
# ***************************************************************************************
# Main
# ***************************************************************************************

def connectToModel():
    """Takes the name of the model to connect to(string) and connects based on current model state"""
    print "in connectToModel"
    project = 'Connect1'
    model = 'rtdemo1'
    # connect to the local project

    projectPath = 'C:/Users/Kellen/OPAL-RT/RT-LABv11_Workspace/Connect1/'
    projectName = os.path.join(projectPath, str(project) + '.llp')
    modelPath = os.path.join(projectPath, 'Simulink/')
    modelName = str(model) + '.mdl'

    # Connects to Project
    RtlabApi.OpenProject(projectName)
    print "Now connected to '%s' project." % projectName

    # Connects to model
    filename = os.path.join(modelPath, modelName)
    # OpalApiPy.SetCurrentModel(filename)
    instanceId, modelState = OpalApiPy.ConnectByName(str(model))
    print "Model State Connected is %s." % modelStateList[modelState]
    print "Now connected to %s model." % modelName
    # print "Model state 1 is %s" %modelState


    return modelState

def connectToModelTest():
    """Takes the name of the model to connect to(string) and connects based on current model state"""
    print "in connectToModel"
    project = 'Connect1'
    model = 'rtdemo1'
    # connect to the local project

    projectPath = 'C:/Users/Kellen/OPAL-RT/RT-LABv11_Workspace/Connect1/'
    projectName = os.path.join(projectPath,str(project) +'.llp')
    modelPath = os.path.join(projectPath,'Simulink/')
    modelName = str(model) + '.mdl'

    #Connects to Project
    RtlabApi.OpenProject(projectName)
    print "Now connected to '%s' project." % projectName

    #Connects to model
    filename = os.path.join(modelPath,modelName)
    # OpalApiPy.SetCurrentModel(filename)
    instanceId,modelState = OpalApiPy.ConnectByName(str(model))
    print "Model State Connected is %s." %modelStateList[modelState]
    print "Now connected to %s model." %modelName
    #print "Model state 1 is %s" %modelState


    try:
        # Acquire Model State, Get system control
        modelState, realTimeMode = OpalApiPy.GetModelState()
        print "Model state is %s'." %modelStateList[modelState]

        # Model Connection Parameters
        systemControl = 0
        # modelName  = 'rtdemo1'
        modelPath  = ''
        exactMatch = 0
        returnOnAmbiquity  = 0

        # Connect API to model if already running
        if modelState == OpalApiPy.MODEL_RUNNING:
            instanceId = OpalApiPy.ConnectByName(str(model))
            print "Now connected to running model %s.\n" %model
            # print ("instanceId is: ", str(instanceId))

        elif (modelState == OpalApiPy.MODEL_LOADABLE):


            # If model is not loaded,load and ask to execute

            realTimeMode = realTimeModeList['Software Sync']
            timeFactor = 1
            OpalApiPy.Load(realTimeMode,timeFactor)
            print "RT Project %s is Loaded." %project
            OpalApiPy.LoadConsole()
            print "Model %s console is loaded" %model

            chooseExecute = raw_input("Would you like to execute model now?  y/n ")
            if chooseExecute == 'y':
                try:
                    print "Now Executing Model"
                    systemControl = 1
                    OpalApiPy.GetSystemControl(systemControl)
                    print "System Control Granted"

                    OpalApiPy.ExecuteConsole()
                    print "Model %s console is executed" %model

                    OpalApiPy.Execute(1)
                    sleepTime = 5
                    sleep(sleepTime)
                    print "Model executed for 5 seconds"
                    systemControl = 0
                    OpalApiPy.GetSystemControl(systemControl)
                    print "System Control Released"
                except:
                    pass
            systemControl = 1
            OpalApiPy.GetSystemControl(systemControl)
            OpalApiPy.ResetConsole()
            print "System Control Granted"
            print "Console is now reset"
            # resets the model after loading
            OpalApiPy.Pause()
            print "Model %s is now paused" %model
            OpalApiPy.Reset()
            print "Model %s is now reset." %model


            systemControl = 0
            OpalApiPy.GetSystemControl(systemControl)
            print "System Control is released"

        elif (modelState == OpalApiPy.MODEL_LOADED) | (modelState == OpalApiPy.MODEL_PAUSED):
            # If model is loaded but not running, execute the model
            try:
                print "Now Executing Model"
                systemControl = 1
                OpalApiPy.GetSystemControl(systemControl)
                print "System Control Granted"

                # Load Simulink and Matlab
                OpalApiPy.LoadConsole()
                print "Model %s console is loaded" % model
                OpalApiPy.ExecuteConsole()
                print "Model %s console is executed" % model
                OpalApiPy.Execute(1)
                sleepTime = 5
                sleep(sleepTime)
                print "Model executed for 5 seconds"

                systemControl = 0
                OpalApiPy.GetSystemControl(systemControl)
                print "System Control Released"

            except:
                pass

            systemControl = 1
            OpalApiPy.GetSystemControl(systemControl)
            OpalApiPy.ResetConsole()
            print "System Control Granted"
            print "Console is now reset"
            # resets the model after loading
            OpalApiPy.Reset()
            print "Model %s is now reset." % model
            print "System Control Released"


            systemControl = 0
            OpalApiPy.GetSystemControl(systemControl)
            print "System Control is released"


        else:
            print "Compile and Assign Model before Loading/Running"





    finally:
        # Disconnect from Model after testing
        OpalApiPy.Disconnect()
        print "Disconnected from %s model" %modelName









