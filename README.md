#**OPAL RT-Lab Python/API Interfacing install instructions**

##This is an API interfacing package for Opal RT-Lab.

The package is developed to run on the default Python 2.6.4 interpreter that is installed with RT-Lab,
and is also compatabile with the Python 2.7 interpreter.
Below are a series of steps to complete for the package
to run from the command line, an IDE of choice, and the RT-Lab python console.


##**Setting up the package for RT-Lab configuration**

1. Download/Clone the OpalApiControl Repository
2. Add the chosen destination for the repository to system PATH and user variable PYTHONPATH.  
  The PYTHONPATH should also have your version of RTLAB in it as well.
  This step allows the OpalApiControl Package to be run in the command line,
  granted your python interpreter is capable of doing so as well.

  The command to import the OpalApiControl package is,
  
  	import OpalApiControl

  To import the associated subpackages, enter 
  
  	from import OpalApiControl.config import *

3. To run the OpalApiControl package from an IDE(like pycharm), add the following,
	
	from OpalApiControlconfig import *

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
and Rt-Lab's interactive console.

NOTE** the package will run without having to import in the python console of your IDE, or Rt-Lab. However,
when using the command line, the OpalApiControl package, and OpalApiControl.config (*all) must be imported.  
This is also true if using the Python Shell(IDLE), as long as the package is imported into your 
Path Browser in within IDLE.



##**Usage with RT-Lab models.**

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

***The package is currently being expanded to allow for model Loading and executing from within the python console***




All of the following package functions require a connection, and for the model to be Loaded so signals and parameters can be accessed.

When model manipulation is complete. It is required that you disconnect from the model using
the built in Api function OpalApiPy.Disconnect(). This module is imported directly from 
the OpalApiControl.config subpackage, or can be imported by the user in the Rt-Lab python console using

	import OpalApiPy


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



