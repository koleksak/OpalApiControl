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


global All_Data
All_Data = acquisitioncontrol.DataList(1)
#Syn_Data = acquisitioncontrol.DataList(2)
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
    global data_set
    global data_ret
    data_set = acquisitioncontrol.StartAcquisitionThread('IEEE39Acq', 'phasor01_IEEE39', All_Data, groups[0],
                                                         "Bus Data Thread Set", 0.0333)
    data_ret = acquisitioncontrol.acquisitionThreadReturn('IEEE39Acq', 'phasor01_IEEE39', All_Data, groups[0],
                                                          "Bus Data Thread Return" , 0.0333)

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
    data_set.start()
    data_ret.start()
    # if 2 in groups:
    #     syn_set.start()
    # if 3 in groups:
    #     load_set.start()
    # #if 4 in groups:
    # #    line_set.start()
    acquire.connectToModel('IEEE39Acq','phasor01_IEEE39')
    OpalApiPy.SetAcqBlockLastVal(0, 1)
    start_time = data_set.simulationTime
    return data_set, data_ret


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
    All_Acq_Data.extend(data_ret.lastAcq)
    #All_Acq_Data.append(psse32.freq)
    #All_Acq_Data.extend(Load_Data.returnLastAcq())
    #All_Acq_Data.extend(Syn_Data.returnLastAcq())

    #print ('Acq Data', All_Acq_Data)
    return All_Acq_Data

def ltb_stream(Vgsinfo):
    """Sends requested data indices for devices to the LTB server using dime"""

    if len(Vgsinfo) == 0:
        logging.warning('<No Device Requests>')
        return False

    else:
        acq_time = time.time()
        mods = Vgsinfo['dev_list']
        for dev in mods:
            if dev == 'sim':
                continue
            idx = Vgsinfo[dev]['vgsvaridx']
            try:
                var_data = acq_data()
            except:
                logging.error('<No simulation data available>')
            else:
                #logging.log('<Setting Varvgs for{} >'.format(dev))
                Varvgs['vars'] = var_data[idx[0]:len(idx)]            #Need to add modified data
                Varvgs['accurate'] = var_data[idx[0]:len(idx)]        #Accurate streaming data
                Varvgs['t'] = data_set.simulationTime-start_time
                print('Time', Varvgs['t'])
                Varvgs['k'] = data_set.simulationTime/0.03333
                print('Steps', Varvgs['k'])
                JsonVarvgs = json.dumps(Varvgs)
                dimec.send_var(dev, 'Varvgs', JsonVarvgs)
                #print ('VarVgs', Varvgs)
                return True

def ltb_stream_sim(SysParam, Varheader, Idxvgs, project, model):
    #sim = {}
    #sim['SysParam'] = SysParam
    #sim['Varheader'] = Varheader
    #sim['Idxvgs'] = Idxvgs
    #sim['Varvgs'] = Varvgs
    global dimec
    dimec = set_dime_connect('sim', 'tcp://127.0.0.1:5678')
    #dimec.exit()
    dimec.broadcast('Varvgs', Varvgs)
    dimec.broadcast('Idxvgs', Idxvgs)
    acquire.connectToModelTest(project, model)
    groups = (1, 2, 3, 4)
    acqthread, retthread = stream_data(groups)
    sleep(0.1)
    while acqthread.is_alive():
        Vgsinfo = varreqs.mod_requests(SysParam)
        ltb_stream(Vgsinfo)
        #sleep(0.0333)


    #dimec.exit()



