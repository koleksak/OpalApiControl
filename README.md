## OpalApiControl
OpalApiControl is a data acquisition, streaming and control interface developed for RT-LAB software packages.  The project was developed for [CURENT](http://curent.utk.edu/) at the University of Tennessee, Knoxville. It serves as a research tool for North American Grid System models analysis.

**OPAL RT-Lab Python/API Interfacing install instructions**

Download the OpalApiControl Package and run the setup.py script.

The package is developed to run on the default Python 2.6.4 interpreter that is installed with RT-Lab,
and is also compatabile with the Python 2.7 interpreter.
hon console.


## **Setting up the package for RT-Lab configuration**

1. Download/Clone the OpalApiControl Repository
2. Add the chosen destination for the repository to system PATH and user variable PYTHONPATH.  
  The PYTHONPATH should also have your version of RTLAB in it as well.

	The OpalApiControl package must be added to the Python Interpreters Library if you wish to use it in the RT-Lab Console(Skip steps 3-5 otherwise).

2. Access to these settings is found in RT-Lab under Window>Preferences>PyDev.
3. In the Interactive Console settings, add,
	```
		import OpalApiControl;	
		from OpalApiControl.config import *
	```
	
	to the end of your initial interpreter commands.
  
4. In the Interpreter-Python section under the libraries tab for each interpreter you wish to use, add the folder containing the OpalApiControl package.

The OpalApiControl package is now ready for use in the command line,and RT-Lab's interactive console if you so choose.

For a detailed overview of the package contents and uses, see the [OpalApiDoc](https://github.com/koleksak/OpalApiControl/blob/dev/OpalAPIDoc.pdf).

***This Project was supported by the Engineering Research Center Program of the National Science Foundation and the Department of Energy under NSF Award Number EEC-1041877 and the CURENT Industry Partnership Program.***

