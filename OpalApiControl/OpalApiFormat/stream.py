"""
VarIDX and VARVGS for LTB PSAT Formatted Data Streaming from ePhasorsim Running Models

"""

import OpalApiPy
import RtlabApi
import dime
from dime import dime
from OpalApiControl.acquisition import acquisitioncontrol
from OpalApiControl.system import acquire
import varreqs
import logging
from time import sleep
import json
import threading



global All_Data
All_Data = {}
VarStore = {}
Varvgs = {}
global dimec
start_time = 0


def stream_data(groups, sim_stop, project, model):
    """Creates Bus,Generator, and Load Data Structure as well as the acquisition threads for dynamic streaming. Threads run
     until the model is paused, then must be run again if further acquisition is required.  Data Lists will be appended to
     granted the Bus_Data, etc, if this module is imported

     groups = (group# tuple, in ascending order)"""

    global data_set_groups
    global data_ret_groups
    data_set_groups = {}
    data_ret_groups = {}
    #acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')

    for num in range(1, len(groups)+1):
        All_Data[num] = acquisitioncontrol.DataList(num)
        data_set_groups[num] = acquisitioncontrol.StartAcquisitionThread(project, model, All_Data[num], groups[num-1],
                                                                         "Data Thread " + str(num) + " Set",
                                                                         0.0333, sim_stop)

        data_ret_groups[num] = acquisitioncontrol.acquisitionThreadReturn(project, model, All_Data[num], groups[num-1],
                                                                          "Data Thread " + str(num) + " Return", 0.0333,
                                                                          sim_stop)

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
        #logging.warning('<No Device Requests>')
        return False

    else:
        mods = Vgsinfo['dev_list']
        for dev in mods:
            if dev == 'sim':
                continue
            idx = Vgsinfo[dev]['vgsvaridx'].pop()
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


def ltb_stream_sim(SysParam, Varheader, Idxvgs, project, model, sim_stop):

    global dimec
    global Event
    Event = {}
    dimec = set_dime_connect('sim', 'tcp://127.0.0.1:5678')
    #dimec.exit()
    dimec.broadcast('Varheader', Varheader)
    dimec.broadcast('Idxvgs', Idxvgs)
    acquire.connectToModelTest(project, model)
    modelState, realTimeMode = OpalApiPy.GetModelState()
    try:
        numgroups = OpalApiPy.GetNumAcqGroups()
    except:
        logging.exception('<No Acquisition groups Available>')
    else:
        groups = list(range(1, numgroups, 1))
        acqthread, retthread = stream_data(groups, sim_stop, project, model)
        #sleep(0.1)
        #while acqthread[1].is_alive():
        while modelState == OpalApiPy.MODEL_PAUSED or modelState == OpalApiPy.MODEL_RUNNING:
            if sim_stop.is_set() is not True and modelState != OpalApiPy.MODEL_PAUSED:
                acquire.transitionToPause()
                #sim_stop.set()
            elif sim_stop.is_set() is True and modelState == OpalApiPy.MODEL_PAUSED:
                acquire.connectToModelTest(project, model)
            else:
                Vgsinfo = varreqs.mod_requests(SysParam, project, model)
                ltb_stream(Vgsinfo)
            modelState, realTimeMode = OpalApiPy.GetModelState()
    print('Sim Ended')
    #acquire.transitionToPause()
    OpalApiPy.Disconnect()