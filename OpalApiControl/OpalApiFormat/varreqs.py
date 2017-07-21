"""Creates SysParam and varvgs subsets per device requests"""

import stream
import logging
import json
import OpalApiPy
import multiprocessing
import os
import time
from OpalApiControl.system import acquire

SysParam = {}
SysName = {}
prereq = 'sim'
global Vgsinfo
Vgsinfo = {}
global ControlP  #List for holding event processing objects
ControlP = []
Vgsinfo['dev_list'] = {}


def mod_requests(SysParamInf, project, model):
    varname = stream.dimec.sync(1)
    dev_list = stream.dimec.get_devices()

    if varname:
        print varname
        vars = stream.dimec.workspace
        if varname == 'Event':
            jsonevent = vars['Event']
            Event = json.loads(jsonevent)
            print Event
            global ControlP
            set_signal_event(Event, ControlP, project, model)   #ControlP is list for processing for each event
            Event['name'] = []
            Event['id'] = []
            Event['action'] = []
            Event['time'] = []
            Event['duration'] = []
            ControlP = []


        if prereq not in dev_list:
            print prereq
            logging.error('<No simulator connected>')

        else:
            for dev_name in dev_list:
                if dev_name == 'sim' or 'Event':
                    continue
                jsonmods = vars[dev_name]
                vars[dev_name] = json.loads(jsonmods)

                if dev_name:
                    param, vgsvaridx, usepmu, limitsample = ([], [], [], [])

                    try:
                        #param = Vgsinfo['dev_list'][dev_name]['param']
                        param = vars[dev_name]['param']


                    except:
                        logging.error('<Param Field Error for {}>'.format(dev_name))

                    try:
                        #vgsvaridx = Vgsinfo['dev_list'][dev_name]['vgsvaridx']
                        vgsvaridx = vars[dev_name]['vgsvaridx']

                    except:
                        logging.error('<Vgsvaridx Field Error for {}>'.format(dev_name))

                    try:
                        #usepmu = Vgsinfo['dev_list'][dev_name]['usepmu']
                        usepmu = vars[dev_name]['usepmu']

                    except:
                        logging.error('<Usepmu Field Error for {}>'.format(dev_name))

                    try:
                        #limitsample = Vgsinfo['dev_list'][dev_name]['limitsample']
                        limitsample = vars[dev_name]['limitsample']

                    except:
                        logging.error('<Limitsample Field Error for {}>'.format(dev_name))

                    if (len(param) == 0) & (len(vgsvaridx) == 0):
                        logging.error('<No Param and Var data requested')
                        break

                    #Send Parameter data
                    if len(param) != 0:
                        for dev in param:
                            if dev == ('BusNames' or 'Areas' or 'Regions'):
                                if dev == 'BusNames':
                                    dev = 'Bus'
                                SysName[dev] = SysParamInf[dev]
                            else:
                                #SysParam[dev] = Vgsinfo['dev_list']['sim']['SysParam'][dev]
                                SysParam[dev] = SysParamInf[dev]

                        #SysParam['nBus'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Bus'])
                        SysParam['nBus'] = len(SysParamInf['Bus'])
                        #SysParam['nLine'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Line'])
                        SysParam['nLine'] = len(SysParamInf['Line'])
                        JsonSysParam = json.dumps(SysParam)
                        JsonSysName = json.dumps(SysName)
                        stream.dimec.send_var(dev_name, 'SysParam', JsonSysParam)
                        stream.dimec.send_var(dev_name, 'SysName', JsonSysName)
                        print('Sent SysParam and SysName to {}'.format(dev_name))

                    if len(vgsvaridx) != 0:
                        if dev_name not in Vgsinfo['dev_list']:
                            keys = Vgsinfo['dev_list'].keys()
                            keys.append(dev_name)
                            Vgsinfo[dev_name] = {}
                            Vgsinfo['dev_list'] = keys
                            #Vgsinfo[dev_name]['location'] = []
                            Vgsinfo[dev_name]['vgsvaridx'] = vgsvaridx
                            Vgsinfo[dev_name]['usepmu'] = usepmu
                            Vgsinfo[dev_name]['limitsample'] = limitsample

                        else:
                            #Vgsinfo['dev_list'].append(dev_name+1)
                            Vgsinfo[dev_name]['vgsvaridx'].append(vgsvaridx)
                            Vgsinfo[dev_name]['usepmu'].append(usepmu)
                            Vgsinfo[dev_name]['limitsample'].append(limitsample)

                    vars[dev_name]['param'] = []
                    vars[dev_name]['vgsvaridx'] = []
                    vars[dev_name]['usepmu'] = []
                    vars[dev_name]['limitsample'] = []

    return Vgsinfo

def set_signal_event(Event, ControlP, project, model):
    """Takes controls from EVENT calls on dime connected modules and
    sends them to the appropriate signal input in ephasorsim corresponding to
    the signal name, which is matched to the ephasorsim name, and port for the signal.

    Event: structure with id,name,t0,action,duration
    ControlP: list of control processes to append to for each event to manage processing"""
    if type(Event['id']) in (int, float):
        Event['id'] = [Event['id']]
    if type(Event['name']) in (int, str, unicode):
        Event['name'] = [Event['name']]
    if type(Event['time']) in (int, float):
        Event['time'] = [Event['time']]
    if type(Event['action']) in (int, float):
        Event['action'] = [Event['action']]
    if type(Event['duration']) in (int, float):
        Event['duration'] = [Event['duration']]

    for item in range(0, len(Event['id'])):
        if Event['name'][item] == 'Bus':
            #Active Fault value == 1, Inactive Fault value == 0(for ePhasorsim)
            signame = 'bus_fault'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index)+ ')'

            ControlP.append(multiprocessing.Process(name=signame + '_event' + str(index), target=opal_control_processor,
                                                    args=(signame, signal, start, end, value, project, model)))
            ControlP[-1].daemon = True
            ControlP[-1].start()

        elif Event['name'][item] == 'Line':
            #Active Fault value == 1, Inactive Fault value == 0(for ePhasorsim)
            signame = 'line_fault'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index) + ')'

            ControlP.append(multiprocessing.Process(name=signame + '_event' + str(index), target=opal_control_processor,
                                                    args=(signame, signal, start, end, value, project, model)))
            ControlP[-1].daemon = True
            ControlP[-1].start()

        elif Event['name'][item] == 'Syn':
            #In-Service value == 1, Out-of-Service value == 0 (for ePhasorsim)
            signame = 'syn_status'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index) + ')'

            ControlP.append(multiprocessing.Process(name=signame + '_event' + str(index), target=opal_control_processor,
                                                    args=(signame, signal, start, end, value, project, model)))
            ControlP[-1].daemon = True
            ControlP[-1].start()


def opal_control_processor(signame, signal, start, end, value, project, model):
    """Handles the event processing for control signal input to ePhasorsim. Spawns new processes to
    deal with the time duration switching needed for event control signals"""

    name = multiprocessing.current_process().name
    print('Process Name', name)
    acquire.connectToModel(project, model)
    projectPath, modelName = OpalApiPy.GetCurrentModel()
    print('ProjectPath', projectPath)
    clockpath = model + '/sm_master/clock/port1'
    print('ClockPath', projectPath)
    current_clock = OpalApiPy.GetSignalsByName(clockpath)
    start_time = time.time()
    sim_time = start_time + current_clock
    #print('CURENTCLOCK', sim_time)
    #print('SIMTIME', sim_time)
    triggered = False   #Keeps track of whether event occured or not
    print('TIME OFFSET TO', sim_time - time.time())
    while (time.time()-start_time) <= end:
        #print('SIMTIME', sim_time)
        if ((time.time()-start_time) >= start) and triggered is False:
            if value == 0 and signame == 'bus_fault' or 'line_fault':
                # Bus Fault trigger for ePhasor sim is Active for value of 1
                value = 1
                try:
                    OpalApiPy.SetSignalsByName(signal, value)
                    triggered = True
                    logging.info('<bus or line fault triggered>')
                except:
                    OpalApiPy.SetSignalsByName(signame, value)
                    triggered = True
                    logging.info('<bus or line fault triggered>')

            elif value == 0 and signame == 'syn_status':
                try:
                    OpalApiPy.SetSignalsByName(signal, value)
                    triggered = True
                    logging.info('<syn status triggered>')
                except:
                    OpalApiPy.SetSignalsByName(signame, value)
                    triggered = True
                    logging.info('<syn status triggered>')

        #current_clock = OpalApiPy.GetSignalsByName(clockpath)
        sim_time = time.time()-start_time

    #Reset Event Signal
    try:
        OpalApiPy.SetSignalsByName(signal, not value)
        logging.info('<event reset>')
    except:
        OpalApiPy.SetSignalsByName(signame, not value)
        logging.info('<event reset>')


#**********************************************************************
"""Originally created for multiple signals to call one event change, adjusted processing to 
be handles by simulator. Below section may be usable for future, more complex simulink block control
"""
# def set_signal_event(Event, ControlP):
#     """Takes controls from EVENT calls on dime connected modules and
#     sends them to the appropriate signal input in ephasorsim corresponding to
#     the signal name, which is matched to the ephasorsim name, and port for the signal.
#
#     Event: structure with id,name,t0,action,duration
#     ControlP: list of control processes to append to for each event to manage processing"""
#     if type(Event['id']) in (int, float):
#         Event['id'] = [Event['id']]
#     if type(Event['name']) in (int, str, unicode):
#         Event['name'] = [Event['name']]
#     if type(Event['time']) in (int, float):
#         Event['time'] = [Event['time']]
#     if type(Event['action']) in (int, float):
#         Event['action'] = [Event['action']]
#     if type(Event['duration']) in (int, float):
#         Event['duration'] = [Event['duration']]
#
#     for item in range(0, len(Event['id'])):
#         if Event['name'][item] == 'Bus':
#             signame = 'bus_fault'
#             sigstart = signame + '.start'
#             sigend = signame + '.end'
#             sigval = signame + '.after'
#             signals = [sigstart, sigend, sigval]
#             value = Event['action'][item]
#             start = Event['time'][item]
#             end = start + Event['duration'][item]
#             index = Event['id'][item]
#
#             set_signal_helper(signame, signals, start, end, value, index)
#
#         elif Event['name'][item] == 'Line':
#             signame = 'bus_fault'
#             sigstart = signame + '.start'
#             sigend = signame + '.end'
#             sigval = signame + '.after'
#             signals = [sigstart, sigend, sigval]
#             value = Event['action'][item]
#             start = Event['time'][item]
#             end = start + Event['duration'][item]
#             index = Event['id'][item]
#             set_signal_helper(signame, signals, start, end, value, index)
#
#         elif Event['name'][item] == 'Syn':
#             signame = 'bus_fault'
#             sigstart = signame + '.start'
#             sigend = signame + '.end'
#             sigval = signame + '.after'
#             signals = [sigstart, sigend, sigval]
#             value = Event['action'][item]
#             start = Event['time'][item]
#             end = start + Event['duration'][item]
#             index = Event['id'][item]
#             set_signal_helper(signame, signals, start, end, value, index)

# def set_signal_helper(signame, signals,value, index):
#     """Helper function for setting ePhasor control input signals"""
#     if value == 0:
#         # Bus Fault trigger for ePhasor sim is Active for value of 1
#         try:
#             values = (start, end, 1)
#             num = 0
#             signalsgroup = []
#             for sig in signal:
#                 if sig == signame + '.start' or sig == signame + '.end':
#                     signalsgroup.append(sig)
#                     continue
#                 else:
#                     sig = sig + '(' + str(index) + ')'
#                     signalsgroup.append(sig)
#                     num += 1
#             OpalApiPy.SetSignalsByName(tuple(signalsgroup), values)
#         except:
#             OpalApiPy.SetSignalsByName(tuple(signals), values)
#
#     else:
#         try:
#             values = (start, end, 0)
#             num = 0
#             signalsgroup = []
#             for sig in signals:
#                 if sig == signame + '.start' or sig == signame + '.end':
#                     signalsgroup.append(sig)
#                     continue
#                 else:
#                     sig = sig + '(' + str(index) + ')'
#                     signalsgroup.append(sig)
#                     num += 1
#             OpalApiPy.SetSignalsByName(tuple(signalsgroup), values)
#         except:
#             OpalApiPy.SetSignalsByName(tuple(signals), values)
#

# def set_signal_helper(signame, signals, start, end, value, index):
#     """Helper function for setting ePhasor control input signals"""
#     if value == 0:
#         # Bus Fault trigger for ePhasor sim is Active for value of 1
#         try:
#             values = (start, end, 1)
#             num = 0
#             signalsgroup = []
#             for sig in signals:
#                 if sig == signame + '.start' or sig == signame + '.end':
#                     signalsgroup.append(sig)
#                     continue
#                 else:
#                     sig = sig + '(' + str(index) + ')'
#                     signalsgroup.append(sig)
#                     num += 1
#             OpalApiPy.SetSignalsByName(tuple(signalsgroup), values)
#         except:
#             OpalApiPy.SetSignalsByName(tuple(signals), values)
#
#     else:
#         try:
#             values = (start, end, 0)
#             num = 0
#             signalsgroup = []
#             for sig in signals:
#                 if sig == signame + '.start' or sig == signame + '.end':
#                     signalsgroup.append(sig)
#                     continue
#                 else:
#                     sig = sig + '(' + str(index) + ')'
#                     signalsgroup.append(sig)
#                     num += 1
#             OpalApiPy.SetSignalsByName(tuple(signalsgroup), values)
#         except:
#             OpalApiPy.SetSignalsByName(tuple(signals), values)
#*********************************************************************************
