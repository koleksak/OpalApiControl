"""
VarIDX and VARVGS for LTB PSAT Formatted Data Streaming from ePhasorsim Running Models

"""

import logging
import threading
from collections import OrderedDict
from time import sleep

import OpalApiPy
import RtlabApi
import dime
import varreqs
from dime import dime
from numpy import array

from unused import acquisitioncontrol, acquire

global All_Data
All_Data = {}
VarStore = {}
Varvgs = {}
global EventQueue
EventQueue = OrderedDict()
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
    condition = threading.Condition()
    kill = False
    #acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')

    for num in range(1, len(groups)+1):
        All_Data[num] = acquisitioncontrol.DataList(num)
        data_set_groups[num] = acquisitioncontrol.StartAcquisitionThread(project, model, All_Data[num], groups[num - 1],
                                                                         "Data Thread " + str(num) + " Set",
                                                                         0.0333, sim_stop, condition)

        data_ret_groups[num] = acquisitioncontrol.acquisitionThreadReturn(project, model, All_Data[num], groups[num - 1],
                                                                          "Data Thread " + str(num) + " Return",
                                                                          0.0333, sim_stop, condition, kill)
        data_set_groups[num].daemon = True
        data_ret_groups[num].daemon = True
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


def ltb_stream(Vgsinfo, acq_thread_groups, groups):
    """Sends requested data indices for devices to the LTB server using dime"""

    if len(Vgsinfo) == 0:
        # logging.warning('<No Device Requests>')
        return False

    else:
        for dev in Vgsinfo.keys():
            if dev == 'sim':
                continue
            idx = Vgsinfo[dev]['vgsvaridx']
            try:
                var_data = acq_data()
                var_data = array(var_data)
            except:
                logging.error('<No simulation data available>')
            else:
                for num in groups:
                    Varvgs['vars'] = var_data[to_python_idx(idx)]            # Need to add modified data
                    Varvgs['accurate'] = var_data[to_python_idx(idx)]        # Accurate streaming data
                    Varvgs['t'] = acq_thread_groups[num].simulationTime
                    Varvgs['k'] = acq_thread_groups[num].simulationTime/0.03333
                    # JsonVarvgs = json.dumps(Varvgs)
                    dimec.send_var(dev, 'Varvgs', Varvgs)
                    logging.log(1, '<Data streamed to {} at {}>'.format(dev, Varvgs['t']))

                    return True


def event_handler(EventQueue, acq_thread_groups):
    """Manages ordered events by time sequence and removes event from queue when triggered
    Handles signals with names following the convention signal(#) where # is the signal device index in
    the model

    Note: If Only one device signal exists, it is named signal without #. Handling such a case can be changed in the
    model, or an update to change signal name if it is unique must be added to this function"""

    event_times = []
    event_times.extend(EventQueue)
    signals = []
    vals = []
    sim_time = acq_thread_groups[1].simulationTime
    if abs(sim_time-event_times[0]) <= 0.01667:
        trig_event = EventQueue.popitem(False)
        # times = [event_times[0]] * (len(trig_event) + 1)
        for sig in trig_event[1:][0]:
            signals.append(sig[1])
            vals.append(sig[3])
        try:
            OpalApiPy.SetSignalsByName(tuple(signals), tuple(vals))
            logging.log(1, '<Event triggered at {}>'.format(acq_thread_groups[1].simulationTime))
            print "Trigger event at ", acq_thread_groups[1].simulationTime

        except:
            logging.error("<Signal input name error. No signals set>")
        return EventQueue, True
    else:
        return EventQueue, False


def ltb_stream_sim(SysParam, Varheader, Idxvgs, project, model, sim_stop):

    global dimec
    global Event
    Event = {}
    print"Waiting for DiME Connection"

    dimec = set_dime_connect('sim', 'tcp://127.0.0.1:5678')

    print"DiME Connected"
    dimec.broadcast('Varheader', Varheader)
    dimec.broadcast('Idxvgs', Idxvgs)
    acquire.connectToModelTest(project, model)
    modelState, realTimeMode = OpalApiPy.GetModelState()
    RtlabApi.OP_EXHAUSTIVE_DISPLAY  #Controller log displays maximimum information for running model
    try:
        numgroups = OpalApiPy.GetNumAcqGroups()
    except:
        logging.exception('<No Acquisition groups Available>')
    else:
        groups = list(range(1, numgroups, 1))
        acq_thread_groups, ret_thread_groups = stream_data(groups, sim_stop, project, model)
        while acq_thread_groups[1].is_alive():
        # while modelState == OpalApiPy.MODEL_PAUSED or modelState == OpalApiPy.MODEL_RUNNING:
            if sim_stop.is_set() is not True and modelState != OpalApiPy.MODEL_PAUSED:
                acquire.transitionToPause()
                #sim_stop.set()
            elif sim_stop.is_set() is True and modelState == OpalApiPy.MODEL_PAUSED:
                acquire.connectToModelTest(project, model)
            else:
                global EventQueue
                Vgsinfo, EventQueue = varreqs.mod_requests(SysParam, EventQueue)
                if ret_thread_groups[1].new_data is True:
                    ltb_stream(Vgsinfo, acq_thread_groups, groups)
                    ret_thread_groups[1].new_data = False
                if len(EventQueue) != 0:
                    EventQueue, trigger = event_handler(EventQueue, acq_thread_groups)
                else:
                    logging.log(1, '<Event queue empty at {}>'.format(acq_thread_groups[1].simulationTime))
            modelState, realTimeMode = OpalApiPy.GetModelState()
    print('Sim Ended')
    dimec.send_var('geovis', 'DONE', 1)
    # acquire.fullDisconnect()
    dimec.exit()
    OpalApiPy.Disconnect()
    return True


def to_python_idx(idx):
    """Offset idx by -1 for MATLAB indices"""
    return [i-1 for i in idx]
