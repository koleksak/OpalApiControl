"""Connects simulator to RT-lab and controls model states.
Handles the control of the ePHASORsim model for data acquisition"""

import os
from numpy import array

import OpalApiPy
import RtlabApi

from consts import *

import logging
logging.basicConfig(level=logging.INFO)


class SimControl(object):
    """RT-LAB simulation control class"""
    def __init__(self, project, model, path=None, t_acq=1./30):
        self.project = project
        self.model = model
        self.path = path
        self.t_acq = t_acq

        self._projectPath = os.path.join(path, str(project) + '/' + str(project) + '.llp')
        self._modelPath = self.model + '.mdl'
        self._instanceID = None

        # Parameters updated by OpalApyPy - no need to modify
        self._modelState = None
        self._realTimeMode = None
        self._allSignals = None

        # Internal states - do not modify
        self._open = False
        self._loaded = False
        self._started = False
        self._lastAcqTime = -1

        # Settings - modifiable
        self._rtMode = SW_SYNC
        self._timeFactor = 1
        self._acqGroup = 1

    def open(self):
        """Open model. Return True if successful, False if failed."""
        if not self._open:
            try:
                RtlabApi.OpenProject(self._projectPath)
                logging.info('Project <{}> opened successful.'.format(self.project))
                self._open = True
            except:
                logging.error("Failed to open to project <{}> model <{}> in path <{}>".format(self.project,
                                                                                                 self.model, self._projectPath))

        self.update_states()
        return self._open

    def update_states(self):
        if self._open:
            self._modelState, self._realTimeMode = OpalApiPy.GetModelState()
        else:
            logging.warning('Open model before updating states.')

    def load(self):
        """Connect to model"""
        if self._loaded:
            self.update_states()
            return True

        retval = False
        if not self._open:
            self.open()

        if self.isRunning:
            try:
                self._instanceID = OpalApiPy.ConnectByName(self.model)
                self._loaded = True
                self._started = True
                retval = True
                logging.info("Connection to running model {} successful.".format(self.model))
            except:
                logging.error("Failed to connect to running model {}.".format(self.model))

        elif self.isLoadable:
            try:
                OpalApiPy.Load(self._rtMode, self._timeFactor)
                OpalApiPy.LoadConsole()
                self._loaded = True
                retval = True
                logging.info("RT-LAB model <{}> and console loading successful.".format(self.model))
            except:
                logging.error("Failed to load model <{}> or console.".format(self.model))

        elif self.isLoaded:
            self._loaded = True
            self.update_states()
            retval = True
        else:
            logging.error('Compile and assign model before loading or running.')

        return retval

    def start(self):
        """Obtain control and start the simulation"""
        if self._started:
            return True

        if not self._loaded:
            self.load()

        logging.info('Now executing model...')

        self.get_system_control(state=1)

        OpalApiPy.ExecuteConsole()
        logging.info("Console is executed")

        OpalApiPy.Execute(1) # TODO: what the argument is
        logging.info("Model <{}> is executed".format(self.model))

        self.update_states()

        logging.info("Model State is {}".format(self.textModelState))

        if self.isLoaded and self.isRunning:
            logging.info("Model Running")
        self._started = True

    def acquisition_signals_parse(self):
        """Parses acquisition signals from main signal description list. Designed for use with setting
        IdxVgs and Varheader in ePhasorsim acquisition port selection"""
        ePHASsignals = list(OpalApiPy.GetSignalsDescription())
        ephasor_port_out = []
        for signal in ePHASsignals:
            if signal[0] == 0:
                ephasor_port_out.append(signal[3])
        OpalApiPy.Disconnect()
        return ephasor_port_out

    def varheader_idxvgs(self):
        """Parse ePHASORsim output ports and generate Varheader and Idxvgs"""
        Varheader = []
        Idxvgs = dict()

        self._allSignals = self.acquisition_signals_parse()

        for signal in self._allSignals:
            if signal[0] == 0:
                Varheader.append(signal[3])

        var_no_idx = []
        for var in Varheader:
            var = var.split('(')
            var_no_idx.append(var[0])

        for idx, item in enumerate(var_no_idx):
            indexed = False
            matlab_idx = idx + 1

            for dev, vars in SysPar.items():
                if item in vars:
                    if dev not in Idxvgs.keys():
                        Idxvgs[dev] = dict()

                    if dev in Idxvgs.keys() and (item not in Idxvgs[dev].keys()):
                        Idxvgs[dev][item] = []

                    if dev in Idxvgs.keys() and item in Idxvgs[dev].keys():
                        Idxvgs[dev][item].append(matlab_idx)
                        indexed = True
                        break
            if not indexed:
                logging.warning('Variable <{}> not added to Idxvgs.'.format(item))

        # Convert to numpy column arrays
        for dev in Idxvgs.keys():
            for var, val in Idxvgs[dev].items():
                Idxvgs[dev][var] = array(val).T

        return Varheader, Idxvgs

    def acquire_data(self):
        """Acquire data from running simulation"""

        if not self._started:
            logging.error('Run model before acquiring data.')

        sample_time_error = 0.5 * self.t_acq
        nextAcqTime = self._lastAcqTime + self.t_acq

        ret_t = 0.
        retval = None

        if self.isRunning:
            try:
                sigVals, monitorInfo, simTimeStep, endFrame = OpalApiPy.GetAcqGroupSyncSignals(self._acqGroup - 1, 0, 0, 1, 1)
            except:
                self._started = False
                logging.debug('Data acquisition exception. Simulation may have completed.')
                ret_t = -1.
            else:
                missedData, offset, self.simulationTime, _ = monitorInfo
                ret_t = self.simulationTime

                if self._lastAcqTime == -1:
                    self._lastAcqTime = self.simulationTime - self.t_acq

                if self.simulationTime < nextAcqTime:  # acquiring too fast
                    pass
                elif self.simulationTime - nextAcqTime < sample_time_error:
                    retval = sigVals
                    self._lastAcqTime = self.simulationTime
                    logging.debug('Data acquired at t = {}'.format(self.simulationTime))
                else:
                    retval = sigVals
                    self._lastAcqTime = self.simulationTime
                    logging.warning('Acquisition sample step missed at t = {}'.format(self.simulationTime))
        else:
            logging.error('Failed to acquire data. Model is not running.')

        return ret_t, int(ret_t/self.t_acq), retval

    def send_event_signals(self, eventQueue):
        """Sends event input data to running ePHASORsim model"""
        signals = []
        vals = []
        eventTimes = []
        trig_event = eventQueue.popitem(False)
        # times = [event_times[0]] * (len(trig_event) + 1)
        for sig in trig_event[1:][0]:
            signals.append(sig[1])
            vals.append(sig[3])
        try:
            OpalApiPy.SetSignalsByName(tuple(signals), tuple(vals))
            logging.log(1, '<Event triggered at {}>'.format(self.simulationTime))
        except:
            logging.error("<Signal input name error. No signals set>")
        eventTimes.extend(eventQueue)
        return eventQueue, eventTimes

    @staticmethod
    def get_system_control(state=None):
        assert (state == 0) or (state == 1)
        OpalApiPy.GetSystemControl(state)
        if state == 1:
            logging.info("System control granted.")
        elif state == 0:
            logging.info("System control dropped.")

    def stop(self):
        """Basic disconnect steps to reset matlab/simulink console, then rtlab console, then disconnect"""
        self.update_states()
        self.get_system_control(state=1)

        if self.isRunning:
            OpalApiPy.PauseConsole()
            OpalApiPy.Pause()
            logging.debug("Model and Console are now paused")

        OpalApiPy.ResetConsole()
        logging.debug("Console is now reset")

        OpalApiPy.Pause()
        logging.debug( "Model %s is now paused")

        OpalApiPy.Reset()
        logging.debug("Model %s is now reset.")
        logging.debug("System Control Released")

        OpalApiPy.GetSystemControl(state=0)
        logging.debug("System Control is released")

        OpalApiPy.Disconnect()
        logging.debug("Disconnected from %s model")

    def pause(self):
        """Pause function. TODO"""
        pass

    def resume(self):
        """Resume function. TODO"""
        pass

    @property
    def textModelState(self):
        return modelStateList[self._modelState]

    @property
    def isRunning(self):
        return True if self._modelState == OpalApiPy.MODEL_RUNNING else False

    @property
    def isLoadable(self):
        return True if self._modelState == OpalApiPy.MODEL_LOADABLE else False

    @property
    def isLoaded(self):
        return True if self._modelState == OpalApiPy.MODEL_LOADED else False

