"""Streaming Object for ePHASORsim running models.  Data is streamed to connected modules on the LTB server"""

from numpy import array
from collections import OrderedDict

from dime import dime

import logging
logging.basicConfig(level=logging.INFO)


class Streaming(object):
    """Class for DiME data streaming"""
    def __init__(self, name, server, ltb_data=None):
        assert ltb_data is not None

        self._name = name
        self._server = server
        self.dimec = dime.Dime(name, server)
        self.ltb_data = ltb_data

        # Internal flags
        self._dime_started = False

        # Internal data
        self.moduleInfo = dict()
        self.lastDevices = list()
        self.eventQueue = OrderedDict()
        self.eventTimes = []

    def start_dime(self):
        if self._dime_started:
            return
        try:
            self.dimec.exit()
            self.dimec.start()
        except:
            self.dimec.start()
        finally:
            self._dime_started = True
            logging.info('DiME client started.')

    def exit_dime(self):
        if self._dime_started:
            try:
                self.dimec.exit()
            except:
                pass
            finally:
                self._dime_started = False
                logging.info('DiME client exit.')

    def send_init(self, recipient='all'):
        """Send Varheader, Idxvgs and SysParam. SysParam is the full set and no longer customizable."""
        devices = self.dimec.get_devices()
        devices.remove('sim')
        if recipient == 'all':
            self.dimec.broadcast('Varheader', self.ltb_data.Varheader)
            self.dimec.broadcast('Idxvgs', self.ltb_data.Idxvgs)
            self.dimec.broadcast('SysParam', self.ltb_data.SysParam)
            logging.info('Varheader, Idxvgs and SysParam broadcast.')
        else:
            if type(recipient) != list:
                recipient = [recipient]
            for item in recipient:
                if item not in devices:
                    continue
                self.dimec.send_var(item, 'Varheader', self.ltb_data.Varheader)
                self.dimec.send_var(item, 'Idxvgs', self.ltb_data.Idxvgs)
                self.dimec.send_var(item, 'SysParam', self.ltb_data.SysParam)
                logging.info('Varheader, Idxvgs and SysParam sent to module <{}>.'.format(item))

    def record_module_init(self, module_name, init_var):
        """Record the variable requests from modules"""
        if self.moduleInfo.has_key(module_name):
            self.moduleInfo[module_name].update(init_var)
        else:
            self.moduleInfo[module_name] = init_var

        vgsvaridx = self.moduleInfo[module_name]['vgsvaridx'].tolist()
        if type(vgsvaridx[0]) == list:
            self.moduleInfo[module_name]['vgsvaridx'] = vgsvaridx[0]
        else:
            self.moduleInfo[module_name]['vgsvaridx'] = vgsvaridx

        self.moduleInfo[module_name]['vgsvaridx'] = [int(i)-1 for i in self.moduleInfo[module_name]['vgsvaridx']]
        logging.info('Init signal from module <{}> recorded.'.format(module_name))

    def handle_event(self, Event):
        """Handle Fault, Breaker, Syn and Load Events"""
        for key in Event.keys():
            if type in (int, float) or (int, str, unicode):
                Event[key] = [Event[key]]
            else:
                logging.warning('Unknown Event key type for <{}>'.format(key))
        event_dict = OrderedDict()
        for item in range(0, len(Event['id'])):
            if Event['name'][item] == 'Bus':
                signame = 'bus_fault'
            if Event['name'][item] == 'Line':
                signame = 'line_fault'
            if Event['name'][item] == 'Syn':
                signame = 'syn_status'

            signal = signame + '(' + str(index) + ')'
            start = Event['time'][item]
            if Event['duration'] == 0:
                end = 1000000
            else:
                end = start + Event['duration'][item]
            index = Event['id'][item]
            value = Event['action'][item]
            event_params = [start, end, signal, signame, value]
            self.eventQueue.update(self.add_event_signal(event_params, event_dict))
            self.eventTimes.extend(self.eventQueue)
            self.eventItems = True

    def add_event_signal(self, event_params, event_dict):
        """Adds event signal parameters to event_queue to be sent to ePHASORsim input controls
        at the start time, and end times provided for each event
        event_params = [start, end, signal, signame, value]"""
        start = event_params[0]
        end = event_params[1]
        signal = event_params[2]
        signame = event_params[3]
        value = event_params[4]

        if start in self.eventQueue.keys():
            self.eventQueue[start].append([start, signal, signame, value])
        else:
            # start_events[start] = [start, signal, signame, value]
            event_dict[start] = [[start, signal, signame, value]]
        logging.info('Adding Event start at <{}> to Event Queue'.format(start))
        if end in self.eventQueue.keys():
            self.eventQueue[end].append([end, signal, signame, ~value])
        else:
            # end_events[end] = [end, signal, signame, not value]
            event_dict[end] = [[end, signal, signame, ~value]]

        logging.info('Adding Event end at <{}> to Event Queue'.format(start))
        return event_dict

    def sync_and_handle(self):
        """Sync until the queue is empty"""

        while True:
            var_name = self.dimec.sync()
            if not var_name:
                break

            current_devices = self.dimec.get_devices()
            workspace = self.dimec.workspace
            var_value = workspace[var_name]

            # send Varheader, SysParam and Idxvgs to modules on the fly
            if set(current_devices) != set(self.lastDevices):
                newDevices = list(current_devices)
                newDevices.remove('sim')
                for item in self.lastDevices:
                    newDevices.remove(item)
                self.send_init(newDevices)

                self.lastDevices = current_devices

            if var_name in current_devices:
                self.record_module_init(var_name, var_value)

            elif var_name == 'Event':
                self.handle_event(var_value)

            else:
                logging.warning('Synced variable {} not handled'.format(var_name))

    def vars_to_modules(self, t, k, varout):
        """Stream the last results to the modules"""
        varout = array(varout)
        for mod in self.moduleInfo.keys():
            idx = self.moduleInfo[mod]['vgsvaridx']
            values = varout[idx]
            Varvgs = {'t': t,
                      'k': k,
                      'vars': array(values),
                      'accurate': array(values),
                      }
            self.dimec.send_var(mod, 'Varvgs', Varvgs)

    def send_done(self):
        self.dimec.broadcast('DONE', 1)
        logging.info('<DONE> signal broadcasted.')

