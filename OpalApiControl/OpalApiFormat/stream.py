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

    global data_set_groups
    global data_ret_groups
    data_set_groups = {}
    data_ret_groups = {}
    acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')

    for num in range(1,len(groups)+1):
        data_set_groups[num] = acquisitioncontrol.StartAcquisitionThread('IEEE39Acq', 'phasor01_IEEE39',
                                                                         All_Data, groups[num-1],
                                                                         "Data Thread " + str(num) + " Set", 0.0333)

        data_ret_groups[num] = acquisitioncontrol.acquisitionThreadReturn('IEEE39Acq', 'phasor01_IEEE39',
                                                                     All_Data, groups[num-1],
                                                                    "Data Thread " + str(num) + " Return", 0.0333)

        data_set_groups[num].start()
        data_ret_groups[num].start()

    #acquire.connectToModel('IEEE39Acq','phasor01_IEEE39')
    OpalApiPy.SetAcqBlockLastVal(0, 1)
    #start_time = data_set.simulationTime
    return data_set_groups, data_ret_groups


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

    all_acq_data = []
    for group in range(1, len(data_ret_groups)+1):
        all_acq_data.extend(data_ret_groups[group].lastAcq)

    return all_acq_data


def ltb_stream(Vgsinfo):
    """Sends requested data indices for devices to the LTB server using dime"""

    if len(Vgsinfo) == 0:
        logging.warning('<No Device Requests>')
        return False

    else:

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
                logging.log(1,'<Setting Varvgs>')
                Varvgs['vars'] = var_data[idx[0]:len(idx)]            #Need to add modified data
                Varvgs['accurate'] = var_data[idx[0]:len(idx)]        #Accurate streaming data
                Varvgs['t'] = data_set_groups[1].simulationTime-start_time
                print('Time', Varvgs['t'])
                Varvgs['k'] = data_set_groups[1].simulationTime/0.03333
                print('Steps', Varvgs['k'])
                JsonVarvgs = json.dumps(Varvgs)
                dimec.send_var(dev, 'Varvgs', JsonVarvgs)

                return True


def ltb_stream_sim(SysParam, Varheader, Idxvgs, project, model):

    global dimec
    dimec = set_dime_connect('sim', 'tcp://127.0.0.1:5678')
    #dimec.exit()
    dimec.broadcast('Varheader', Varheader)
    dimec.broadcast('Idxvgs', Idxvgs)
    acquire.connectToModelTest(project, model)
    groups = (1, 2, 3, 4)
    acqthread, retthread = stream_data(groups)
    sleep(0.1)
    while acqthread[1].is_alive():
        Vgsinfo = varreqs.mod_requests(SysParam)
        ltb_stream(Vgsinfo)




