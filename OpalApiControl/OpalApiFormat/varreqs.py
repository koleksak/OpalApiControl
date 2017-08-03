"""Creates SysParam and varvgs subsets per device requests"""

import stream
import logging
import json
import OpalApiPy
import multiprocessing
import os
import time
from collections import OrderedDict
from collections import deque
from OpalApiControl.system import acquire
from numpy import array, ndarray


global Vgsinfo
global EventQueue

SysParam = {}
SysName = {}
Vgsinfo = {}
EventQueue = OrderedDict()

prereq = 'sim'


def mod_requests(SysParamInf, EventQueue):
    varname = stream.dimec.sync(1)
    dev_list = stream.dimec.get_devices()

    if varname:
        workspace = stream.dimec.workspace
        if varname == 'Event':
            jsonevent = workspace['Event']
            try:
                Event = json.loads(jsonevent)
            except:
                logging.warning('<missed dev_name conversion>')
            else:
                EventQueue.update(add_signal_event(Event))
                #print "Event QUEUE ", EventQueue
                workspace.pop('Event')
                # Event['name'] = []
                # Event['id'] = []
                # Event['action'] = []
                # Event['time'] = []
                # Event['duration'] = []

        if prereq not in dev_list:
            logging.error('<No simulator connected>')

        else:
            for mod in dev_list:
                if mod == 'sim':
                    continue
                else:

                    # if no initialization received then continue
                    if mod not in workspace.keys():
                        continue
                    logging.info('Process initialization from <>'.format(mod))

                    param = workspace[mod].get('param', None)
                    vgsvaridx = workspace[mod].get('vgsvaridx', None)
                    usepmu = workspace[mod].get('usepmu', None)
                    limitsample = workspace[mod].get('limitsample', None)

                    if (not param) and (not vgsvaridx):
                        logging.warning('Module <> sends no param or varidx request. Request ignored.'.format(mod))
                        continue

                    # Send Parameter data
                    if param:
                        for dev in param:
                            if dev == ('BusNames' or 'Areas' or 'Regions'):
                                if dev == 'BusNames':
                                    dev = 'Bus'
                                SysName[dev] = SysParamInf[dev]
                            else:
                                if dev in SysParamInf.keys():
                                    SysParam[dev] = SysParamInf[dev]

                        # SysParam['nBus'] = len(SysParamInf['Bus'])
                        # SysParam['nLine'] = len(SysParamInf['Line'])

                        # TODO: fix it for SE
                        # JsonSysParam = json.dumps(SysParam)
                        # JsonSysName = json.dumps(SysName)

                        stream.dimec.send_var(mod, 'SysParam', SysParam)
                        stream.dimec.send_var(mod, 'SysName', SysName)
                        logging.info('Sent SysParam and SysName to {}'.format(mod))

                    # Record `vgsvaridx` to `Vgsinfo`
                    if vgsvaridx is not None:
                        # Convert `varvgsidx` to a list of integers
                        if type(vgsvaridx) == ndarray:
                            vgsvaridx = vgsvaridx.tolist()
                        if type(vgsvaridx[0]) == list:
                            if len(vgsvaridx) >= 1:
                                vgsvaridx = vgsvaridx[0]
                        vgsvaridx = to_int_list(vgsvaridx)

                        # Create in the dictionary if not exist. Otherwise update.
                        if mod not in Vgsinfo.keys():
                            Vgsinfo[mod] = {'vgsvaridx': vgsvaridx,
                                                    'usepmu': usepmu,
                                                    'limitsample': limitsample
                                                    }
                        else:
                            Vgsinfo[mod].update({'vgsvaridx': vgsvaridx,
                                                          'usepmu': usepmu,
                                                          'limitsample': limitsample
                                                          })
                    workspace.pop(mod)
    return Vgsinfo, EventQueue


def add_signal_event(Event):
    """Takes controls from EVENT calls on dime connected modules and
    sends them to the appropriate signal input in ephasorsim corresponding to
    the signal name, which is matched to the ephasorsim name, and port for the signal.

    Event: structure with id,name,t0,action,duration
    """

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

    Event_Dict = OrderedDict()

    for item in range(0, len(Event['id'])):
        if Event['name'][item] == 'Bus':
            # Active Fault value == 1, Inactive Fault value == 0(for ePhasorsim)
            signame = 'bus_fault'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index) + ')'
            EventQueue.update(add_event_helper(start, end, signal, signame, value, Event_Dict))

        elif Event['name'][item] == 'Line':
            # Active Fault value == 1, Inactive Fault value == 0(for ePhasorsim)
            signame = 'line_fault'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index) + ')'
            EventQueue.update(add_event_helper(start, end, signal, signame, value, Event_Dict))


        elif Event['name'][item] == 'Syn':
            # In-Service value == 1, Out-of-Service value == 0 (for ePhasorsim)
            signame = 'syn_status'
            value = Event['action'][item]
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            signal = signame + '(' + str(index) + ')'
            EventQueue.update(add_event_helper(start, end, signal, signame, value, Event_Dict))

    return EventQueue


def add_event_helper(start, end, signal, signame, value, Event_Dict):
    """Helps add event to Event_Dict"""
    # start_events = {}
    end_events = {}
    if start in EventQueue.keys():
        EventQueue[start].append([start, signal, signame, value])
    else:
        # start_events[start] = [start, signal, signame, value]
        Event_Dict[start] = [[start, signal, signame, value]]

    if end in EventQueue.keys():
        EventQueue[end].append([end, signal, signame, ~value])
    else:
        # end_events[end] = [end, signal, signame, not value]
        Event_Dict[end] = [[end, signal, signame, ~value]]
    return Event_Dict


def to_int_list(idx):
    """Convert a list to a list of integers. Round down to the nearest integer."""

    ret = []
    for item in idx:
        v = int(item)
        ret.append(v)

    return ret
