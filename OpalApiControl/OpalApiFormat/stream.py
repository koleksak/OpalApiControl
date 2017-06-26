"""
VarIDX and VARVGS for LTB PSAT Formatted Data Streaming from ePhasorsim Running Models

"""

import OpalApiPy
import dime
from dime import dime
from OpalApiControl.acquisition import acquisitioncontrol
from OpalApiControl.system import acquire
import psse32
import varreqs
import logging
import time
from time import sleep
import json
import idxvgs
from pymatbridge import Matlab
import stream
import threading


global Bus_Data
Bus_Data = acquisitioncontrol.DataList(1)
BusIDX = {}
busvolt = []
busang = []
#Syn_Data = acquisitioncontrol.DataList(2)
SynIDX = {}
synang = []
synspeed = []
syne1d = []
syne1q = []
syne2d = []
syne2q = []
synpsid = []
synpsiq = []
synact = []
synreact = []
ExcIDX = {}
excVref = []
excVmag = []

#Load_Data = acquisitioncontrol.DataList(3)
VarStore = {}
Varvgs = {}
global dimec
start_time = 0


def stream_data(groups):
    """Creates Bus,Generator, and Load Data Structure as well as the acquisition threads for dynamic streaming. Threads run
     until the model is paused, then must be run again if further acquisition is required.  Data Lists will be appended to
     granted the Bus_Data, etc, if this module is imported

     groups = (group# tuple, in ascending order)"""
    #if 1 in groups:
    global bus_set
    bus_set = acquisitioncontrol.StartAcquisitionThread('IEEE39Acq', 'phasor01_IEEE39', Bus_Data, groups[0],
                                                         "Bus Data Thread Set", 0.33)
    print('Data Thread started')
    # if 2 in groups:
    #     syn_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Syn_Data, groups[1],
    #                                                    "Generator Data Thread Set", 0.33)
    # if 3 in groups:
    #     load_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Load_Data, groups[2],
    #                                                    "Load Data Thread Set", 0.33)
    # if 4 in groups:
    #     line_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Load_Data, groups[3],
    #                                                      "Load Data Thread Set", 0.33)
    #if 1 in groups:
    bus_set.start()
    # if 2 in groups:
    #     syn_set.start()
    # if 3 in groups:
    #     load_set.start()
    # #if 4 in groups:
    # #    line_set.start()
    acquire.connectToModel('IEEE39Acq','phasor01_IEEE39')
    OpalApiPy.SetAcqBlockLastVal(0, 1)
    start_time = bus_set.simulationTime
    return bus_set


def set_dime_connect(dev, port):
    """Enter module name to connect, along with the port established by dime connection."""

    try:
        global dimec
        dimec = dime.Dime(dev, port)
        dimec.start()
        sleep(0.1)

    except:
        try:
            dimec.exit()
            dimec.start()

        except:
            logging.warning('<dime connection not established>')
            return False
    else:
        #dimec.exit()
        logging.info('<dime connection established>')
        return dimec


def acq_data():
    """Constructs acquisition list for data server. Slight re-ordering is done for Bus P and Q(Must append Syn,Load P and Q)"""
    All_Acq_Data = []
    #print('*************', Bus_Data.returnLastAcq())
    All_Acq_Data.extend(Bus_Data.returnLastAcq())
    #All_Acq_Data.append(psse32.freq)
    #All_Acq_Data.extend(Load_Data.returnLastAcq())
    #All_Acq_Data.extend(Syn_Data.returnLastAcq())

    #print ('Acq Data', All_Acq_Data)
    return All_Acq_Data

def ltb_stream(Vgsinfo):
    """Sends requested data indices for devices to the LTB server using dime"""

    if Vgsinfo == None:
        logging.warning('<No Devices Requesting>')
        return False

    else:
        acq_time = time.time()
        for dev in varreqs.Vgsinfo['dev_list'].keys():
            if dev == 'sim':
                continue
            idx = varreqs.Vgsinfo['dev_list'][dev]['vgsvaridx']
            try:
                var_data = acq_data()
            except:
                logging.error('<No simulation data available>')
            else:
                #logging.log('<Setting Varvgs for{} >'.format(dev))
                Varvgs['vars'] = var_data[idx[0]:len(idx)]            #Need to add modified data
                Varvgs['accurate'] = var_data[idx[0]:len(idx)]        #Accurate streaming data
                Varvgs['t'] = bus_set.simulationTime-start_time
                print('Time', Varvgs['t'])
                Varvgs['k'] = bus_set.simulationTime/0.03333
                print('Steps', Varvgs['k'])
                JsonVarvgs = json.dumps(Varvgs)
                dimec.send_var(dev, 'Varvgs', JsonVarvgs)
                #print ('VarVgs', Varvgs)
                return True

def ltb_stream_sim(SysParam, Varheader, Idxvgs, project, model):
    sim = {}
    sim['SysParam'] = SysParam
    sim['Varheader'] = Varheader
    sim['Idxvgs'] = Idxvgs
    sim['Varvgs'] = Varvgs
    dimec = set_dime_connect('sim', 'tcp://127.0.0.1:5678')
    #dimec.exit()
    dimec.send_var('sim', 'sim', sim)
    #dimec.send_var('geo', 'sim', sim)
    acquire.connectToModelTest(project, model)
    modelState, realtimemode = OpalApiPy.GetModelState()
    groups = (1, 2, 3, 4)
    acqthread = stream_data(groups)
    sleep(0.1)
    #print ('**********modelState*********', modelState)
    while acqthread.is_alive():
        Vgsinfo = varreqs.mod_requests()
        ltb_stream(Vgsinfo)
        modelState, realtimemode = OpalApiPy.GetModelState()

    #dimec.exit()



