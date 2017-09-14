"""Streaming Object for ePHASORsim running models.  Data is streamed to connected modules on the LTB server"""

from numpy import array, ndarray
from collections import OrderedDict

from dime import dime
import logging


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
        self.storedEvents = EventQueue()

        self.start_dime()

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
            logging.info('DiME client started on {}.'.format(self._server))

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

        vgsvaridx = self.moduleInfo[module_name]['vgsvaridx']

        # convert to list from ndarray or numbers
        if type(vgsvaridx) == ndarray:
            vgsvaridx = vgsvaridx.tolist()
        elif type (vgsvaridx) == list:
            pass
        else:
            vgsvaridx = [vgsvaridx]

        if type(vgsvaridx[0]) == list:
            self.moduleInfo[module_name]['vgsvaridx'] = vgsvaridx[0]
        else:
            self.moduleInfo[module_name]['vgsvaridx'] = vgsvaridx

        self.moduleInfo[module_name]['vgsvaridx'] = [int(i)-1 for i in self.moduleInfo[module_name]['vgsvaridx']]
        logging.info('Init signal from module <{}> recorded.'.format(module_name))

    @property
    def simTime(self):
        return self.ltb_data.sim.simulationTime

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
                self.storedEvents.add_event(var_value)

            else:
                logging.warning('Synced variable {} not handled'.format(var_name))

        # Do this at each time step - check events and set port signals
        if not self.storedEvents.isEmpty:
            signal, value = self.storedEvents.get_events_at_time(self.simTime)
            if signal:
                self.ltb_data.sim.send_event_signals(signal, value)

    def vars_to_modules(self, t, k, varout):
        """Stream the last results to the modules"""
        varout = array(varout)
        for mod in self.moduleInfo.keys():
            idx = self.moduleInfo[mod]['vgsvaridx']
            # TODO: if idx is out of bound
            values = varout[idx]
            Varvgs = {'t': t,
                      'k': k,
                      'vars': array(values),
                      'accurate': array(values),
                      }
            self.dimec.send_var(mod, 'Varvgs', Varvgs)


    def run(self):
        """Start automatic data acquisition and streaming"""
        while True:
            self.sync_and_handle()
            t, k, varout = self.ltb_data.sim.acquire_data()
            if t == -1:  # end of data acquisition
                self.send_done()
                self.exit_dime()
                break
            if not varout:
                continue
            else:
                self.vars_to_modules(t, k, varout)

    def send_done(self):
        """Broadcast `DONE` signal"""
        self.dimec.broadcast('DONE', 1)
        logging.info('<DONE> signal broadcasted.')

    @property
    def has_modules(self):
        return True if len(self.moduleInfo.keys()) else False


class EventQueue(object):
    """Simple event queue"""
    def __init__(self):
        self._signame = []
        self._signal = []  # signame + id
        self._start = []
        # self._end = []
        self._value = []

    @property
    def isEmpty(self):
        return True if not len(self._start) else False

    def add_event(self, Event):
        assert type(Event) == dict
        if not Event.has_key('name'):
            logging.warning('Event is missing <name> field. Event is discarded.')
            return
        elif not Event.has_key('id'):
            logging.warning('Event is missing <id> field. Event is discarded.')
            return
        elif not Event.has_key('time'):
            logging.warning('Event is missing <time> field. Event is discarded.')
            return
        elif not Event.has_key('duration'):
            logging.warning('Event is missing <duration> field. Using +inf duration.')

        # convert to iterables
        for key in Event.keys():
            if type(Event[key]) in (int, float, str, unicode):
                Event[key] = [Event[key]]
                Event[key] = Event[key][0].tolist()  # TODO: check
            elif type(Event[key]) is list:
                continue
            elif type(Event[key]) is ndarray:
                Event[key] = Event[key][0].tolist()
            else:
                logging.error('Unexpected Event key <{}> type <{}>'.format(key, type(Event[key])))

        # add and sort
        for idx, item in enumerate(Event['id']):
            if Event['name'][idx] == 'Bus':
                signame = 'bus_fault'
            elif Event['name'][idx] == 'Line':
                signame = 'line_fault'
            elif Event['name'][idx] == 'Syn':
                signame = 'syn_status'
            else:
                logging.warning('Unsupported event name <{}>'.format(Event['name'][idx]))
                continue

            signal = signame + '({})'.format(int(item))
            start = float(Event['time'][idx])
            if Event['duration'][idx] == 0:
                end = 1000000.
            else:
                end = start + Event['duration'][idx]
            value = int(Event['action'][idx])

            # for start time
            insert_idx = get_insert_idx(self._start, start)
            self.insert_by_idx(insert_idx, start, signal, value, signame=signame)

            # for end time
            insert_idx = get_insert_idx(self._start, end)
            self.insert_by_idx(insert_idx, end, signal, neg(value), signame=signame)

    def remove_by_idx(self, idx):
        """Remove a single event by idx"""
        try:
            self._start.pop(idx)
            self._signal.pop(idx)
            self._signame.pop(idx)
            self._value.pop(idx)
        except:
            print(self._start)
            print(self._signal)
            print(self._signame)
            print(self._value)

    def insert_by_idx(self, insert_idx, start, signal, value, signame=None):
        """Insert a single event to `idx`"""
        if (not start) or (not signal):
            logging.error('Event data is not complete.')
            return
        self._start.insert(insert_idx, start)
        self._signal.insert(insert_idx, signal)
        self._value.insert(insert_idx, value)
        if signame:
            self._signame.insert(insert_idx, signame)

    def get_events_at_time(self, simTime, t_acq=1./30):
        """Return (signal, value) in at `simTime`. signal and value are in lists"""
        signal, value, idxes = list(), list(), list()
        for idx, eventTime in enumerate(self._start):
            if abs(simTime - eventTime) <= 0.5 * t_acq:
                idxes.append(idx)
                signal.append(self._signal[idx])
                value.append(self._value[idx])
                continue
            elif simTime - eventTime >= 0.5 * t_acq:  # time `eventTime` has passed
                idxes.append(idx)
            elif simTime - eventTime < -0.5 * t_acq:
                break

        idxes = sorted(idxes, reverse=True)
        for event_idx in idxes:
            self.remove_by_idx(event_idx)
        return signal, value


def get_insert_idx(sorted_list, data):
    """Get the index to insert `data` to `sorted_list` in ascending order"""
    assert type(sorted_list) == list
    idx = 0
    for item in sorted_list:
        if item < data:
            idx += 1
            continue
    return idx


def neg(num):
    """Return negative value of `number`"""
    if num == 0.:
        return 1
    elif num == 1.:
        return 0
    else:
        return not num
