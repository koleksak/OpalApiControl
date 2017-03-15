## This is an API interfacing package for Opal RT-Lab.

**OPAL RT-Lab Python/API Interfacing install instructions**

Download the OpalApiControl Package and run the setup.py script.

The package is developed to run on the default Python 2.6.4 interpreter that is installed with RT-Lab,
and is also compatabile with the Python 2.7 interpreter.
Below are a series of steps to complete for the package
to run from the command line, an IDE of choice, and the RT-Lab python console.


## **Setting up the package for RT-Lab configuration**

1. Download/Clone the OpalApiControl Repository
2. Add the chosen destination for the repository to system PATH and user variable PYTHONPATH.  
  The PYTHONPATH should also have your version of RTLAB in it as well.
  This step allows the OpalApiControl Package to be run in the command line,
  granted your python interpreter is capable of doing so as well.

  The command to import the OpalApiControl package is,
  
  	import OpalApiControl

  To import the associated subpackages, enter 
  
  	from OpalApiControl.config import *

3. To run the OpalApiControl package from an IDE(like pycharm), add the following,
	
	from OpalApiControl.config import *

to the Console->Python Console starting script in your IDE.
The OpalApiControl package can now be run in the Python console of your chosen IDE.


Including the package into the RT-Lab Python Library and interpreter.

1. The OpalApiControl package must be added to the Python Interpreters Library for each interpreter you wish to use.
2. Access to these settings is found in RT-Lab under Window>Preferences>PyDev.
3. In the Interactive Console settings, add,

	import OpalApiControl;from OpalApiControl.config import *

  to the end of your initial interpreter commands.
4. In the Interpreter-Python section under the libraries tab for each interpreter you wish to use,  
   add the folder containing the OpalApiControl package.

The OpalApiControl package is now ready for use in the command line, your IDE(example using PyCharm),
and RT-Lab's interactive console.

NOTE *the package will run without having to import in the python console of your IDE, or Rt-Lab. However,
when using the command line, the OpalApiControl package, and OpalApiControl.config (\*all) must be imported.  
This is also true if using the Python Shell(IDLE), as long as the package is imported into your 
Path Browser in within IDLE.*



## **Usage with RT-Lab models.**

The model for which you wish to connect must be compiled in RT-Lab before connecting to the API.
Currently, four OpalApiControl subpackages can be used for model interaction.(ommiting the config package
which imports all subpackages).


**aqcuire Package**

Connects to the chosen model by project name and model name as is specified in your RT-Lab project.
It is used as follows.

	acquire.connectToModel('projectName','modelName')

The above will state whether the connection was successful or not, including the model 
and project to which it is now connected.  It will also display the current 
state(LOADED,PAUSED,RUNNING) of the model upon connection.

To load or execute the model call the function,
	
	acquire.connectToModelTest('projectName','modelName')
	
If the model is already loaded, it will execute, otherwise, you will be asked if you would like to execute the model at the 
time of the call.

All of the following package functions require a connection, and for the model to be Loaded so signals and parameters can be accessed.

When model manipulation is complete. It is required that you disconnect from the model using
the built in Api function OpalApiPy.Disconnect(). This module is imported directly from 
the OpalApiControl.config subpackage, or can be imported by the user in the Rt-Lab python console using

	import OpalApiPy

**acquisitioncontrolPackage**

This is the main package for data acquisition of RT-Lab acquisition group signals, and dynamic signals added to the group list.
Acquisitions are started with threads, which call the 'acquire.connectToModel('projectName','modelName')' function for the proper
model for you.  This connection is made when instantating the data acquisition thread.  A sample of creating the DataList object
required for storing acquisition data, and choosing sampling intervals at which to acquire is shown below,


	dataStruct1 = acquisitioncontrol.DataList(1)    # sets up the data structure to the assigned group signals in group 1
	structSet = acquisitioncontrol.StartAcquisitionThread('projectName','modelName',dataStruct1,1,"AcqThread Set",0.03333)
	structSet.start()    #starts acquisition thread. acquisition thread exits when the model is paused or stopped


"structSet = ..." creates an acquisition thread object initialized by the project, model, DataList(to store data), group number,
acquire name, and sampling interval(30/s in this case).

Access to the DataList object acquired values can be done using the DataList object created(example dataStruct1),

	dataStruc1[index]

For accessing a list of all group signals for a chosen index, or

	dataStruct1[index][signal#]


to access a particular signal value for a chosen sampling index.

Also builtin to the DataList object is a method to return the last acquired data list(this is the primary funciton of the
acquisitionThreadReturn() discussed next). To return the last acquired DataList,

	dataStruct1.returnLastAcq()

User's may create their own acquisition return functions for specific use, however the acquisitionThreadReturn() discussed below
will continuously return fetch the last acquired DataList values for the chosen sampling interval which was defined when setting the 
initial acquisition thread.

For returning acquired data, use,


	structRet = acquisition.acquisitionThreadReturn('projectName','modelName',dataStruct1,1,"AcqThread Set",1)
	structRet.start()


The last parameter of the funciton above is 1 if the sampling interval is to be the same as the structSet object. 
This is a built in thread which can adjusted for real time data return from the dataStruct1 object. An example of returning data
which is not the last acquired list is shown below, with the understanding that the data Set and data Return threads are started,

	#prints the values for signal 1 in the first 100 samples
	for i in range(0,100)
	print(structRet.dataList.dataValues[0][i])


*A quick note about acquisition calls.  Once the acquisition thread exits, the structSet must be reinitialized with the same
DataList to store the acquisitions. This will add new data to exisiting acquisitions. Same goes for data return objects*


**signalcontrolPackage**

This package accesses dynamic signals within RT-Lab.  The two types of dynamic signals are,
- Control Signals(read-and writeable)
- Signals(non-control,read-only)

The control signals can be viewed with the following package instruction

	signalcontrol.showControlSignals()

This lists the Control Signals in order by SubSystemID Value.
(SubSystemID associated signal values differentiate control signals from non-control which just have signal ID's))
The ID values are based on the signal order as is specified by your models OpComm Block and can be 
confirmed in the sc_console submenu in your model.

To change control signals, when the model is loaded, or running, a tuple of signal ID's and signal values must be passed. For instance

	signalIDs =  (1,2,3,4)
	signalVals = (10,20,30,40)

	signalcontrol.setControlSignals(signalIDS,signalVals)

Run the showControlSignals() function again to confirm your changes.


To read the non-control dynamic signals, enter the following.

	signalcontrol.showSignals()

This prints a list of the remaining dynamic signals in order of ID number. These values are read only, 
and generally will be set to zero before the model starts running.  The ID number of these non-control signal starts atthe number following the last control signal.


Within the signal control package, getSignalsDict() and getControlSignalsDict() will return a key-value pair based on
the ID number and Value of the signals.  This dictionary can be returned for data extraction from the models values.


**parametercontrol Package**

The parametercontrol package functions much like the signalcontrol package.
It is unclear as to which order parameters are assigned in RT-Lab. But the proper parameter can be matched by its name and ID as shown in the showParameterValues() function.

To show a list of available parameters,

	parametercontrol.showParameterValues()

To change parameter values,

	paramIDS = (5,6,7,8)
	values   = (50,60,70,80)
	parametercontrol.setParameterValues(paramIDS,values)

The setParameterValues() function can also take a single ID and value as its input.


The getParametersDict() function returns a dictionary with key-value pairs based on the parameter ID and value.



