"""Connects simulator to RT-lab and controls model states.
Handles the control of the ePHASORsim model for data acquisition"""

import logging
import os

import OpalApiPy
import RtlabApi

import itertools
from consts import *
import numpy
from numpy import array
from numpy import dot
from numpy import exp
from numpy import subtract
from numpy import multiply
from numpy import real
from numpy import imag
from numpy import ndarray



class SimControl(object):
    """RT-LAB simulation control class"""
    def __init__(self,project, model, path=None, t_acq=1./30):
        self.project = project
        self.model = model
        self.path = path
        self.t_acq = t_acq
        self.IdxvgsStore = None
        self.branch_power = None
        self.Settings = None

        self._projectPath = os.path.join(path, str(project) + '/' + str(project) + '.llp')
        self._modelPath = self.model + '.mdl'
        self._instanceID = None

        # Parameters updated by OpalApyPy - no need to modify
        self._modelState = None
        self._realTimeMode = None
        self._allSignals = None
        self.simulationTime = 0.

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
                logging.info("Connection to RUNNING model {} successful.".format(self.model))
            except:
                logging.error("Failed to connect to RUNNING model {}.".format(self.model))

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
            logging.info("Connection to LOADED model {} successful.".format(self.model))

        elif self.isPaused:
            OpalApiPy.LoadConsole()
            self._loaded = True
            self.update_states()
            retval = True
            logging.info("Connection to PAUSED model {} successful.".format(self.model))


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

        OpalApiPy.Execute(1) #(Argument * model time factor) = Execution Rate. 1 for real-time.
        logging.info("Model <{}> is executed".format(self.model))

        self.update_states()

        logging.info("Model State is {}".format(self.textModelState))

        if self.isLoaded and self.isRunning:
            logging.info("Model Running")
        self._started = True

    def set_settings(self,Settings):
        self.Settings = Settings

    def varheader_idxvgs(self):
        """Parse ePHASORsim output ports and generate Varheader and Idxvgs"""
        Varheader = []
        Idxvgs = dict()

        self._allSignals = list(OpalApiPy.GetSignalsDescription())

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
            #TODO: Add Line Power data that is calculated outside of ePHASORsim
            if not indexed:
                logging.warning('Variable <{}> not added to Idxvgs.'.format(item))

        # Convert to numpy column arrays
        for dev in Idxvgs.keys():
            for var, val in Idxvgs[dev].items():
                Idxvgs[dev][var] = array(val).T
        self.IdxvgsStore = Idxvgs

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
                elif abs(self.simulationTime - nextAcqTime)  <= sample_time_error:
                    retval = sigVals
                    # self.branch_power = self.calc_branch_power(sigVals)
                    # if self.branch_power == None:
                    #     pass
                    # else:
                    #     newvals = list(retval)
                    #     newvals.extend(self.branch_power)
                    #     retval = tuple(newvals)

                    self._lastAcqTime = self.simulationTime
                    _, rem = divmod(self._lastAcqTime, 5)  # show info every 5 seconds
                    if abs(rem) < self.t_acq:
                        logging.debug('Data acquired at t = {}'.format(self.simulationTime))

                    ret_t = self.simulationTime
                elif self.simulationTime - self._lastAcqTime > sample_time_error + 0.001:
                    retval = sigVals
                    # self.branch_power = self.calc_branch_power(sigVals)
                    # if self.branch_power == None:
                    #     pass
                    # else:
                    #     newvals = list(retval)
                    #     newvals.extend(self.branch_power)
                    #     retval = tuple(newvals)
                    logging.warning('Under-sampling occurred at t = {}'.format(self.simulationTime))
                    self._lastAcqTime = self.simulationTime

                    ret_t = self.simulationTime


        return ret_t, int(ret_t/self.t_acq), retval

    def send_event_signals(self, signal, value):
        try:
            sigs = tuple(signal)
            vals = tuple(value)
            OpalApiPy.SetSignalsByName(sigs, vals)
            logging.info('<{}> Event triggered at t = {}'.format(len(sigs), self.simulationTime))
        except:
            logging.error("<Signal input name error. No signals set>")

    def calc_branch_power(self, sigVals):
        """calculates branch P,Q,S from acquired data to be added to the acquired data list"""
        Pij = []
        Qij = []
        Sij = []
        Pji = []
        Qji = []
        Sji = []
        Bus_P = []
        Bus_Q = []
        retval = []

        try:
            line_current = array(sigVals[self.IdxvgsStore['Line']['Iij'][0]:self.IdxvgsStore['Line']['Iij'][-1]])
            line_angle = array(sigVals[self.IdxvgsStore['Line']['Iij_ang'][0]:self.IdxvgsStore['Line']['Iij_ang'][-1]])
            bus_mag = array(sigVals[self.IdxvgsStore['Bus']['V'][0]:self.IdxvgsStore['Bus']['V'][-1]])
            bus_ang = array(sigVals[self.IdxvgsStore['Bus']['theta'][0]:self.IdxvgsStore['Bus']['theta'][-1]])
        except:
            logging.error("<Missing Idxvgs for Line current, angle or Bus Magnitude. Branch power not added>")
            return None
        else:
            for bus in self.Settings.LineBusMatij:
                phi = []
                idx = self.Settings.LineBusMatij[bus]
                try:   #TODO:FIXBUG Indexing
                    Imag = line_current[idx]
                except:
                    break
                Iang = line_angle[idx]
                S = multiply(bus_mag[bus-1],Imag)
                phi_diff = subtract((bus_ang[bus-1]),Iang)
                for ang in phi_diff:
                    phi.append(exp(1j*ang))
                phi = array(phi)
                S_ = multiply(S,phi)
                P = real(S_)
                Q = imag(S_)
                Bus_P.append(sum(P))
                Bus_Q.append(sum(Q))
                Pij.extend(P)
                Qij.extend(Q)
                Sij.extend(S)

            for bus in self.Settings.LineBusMatij:
                phi = []
                idx = self.Settings.LineBusMatji[bus]
                try:
                    Imag = line_current[idx]
                except:
                    break
                Iang = line_angle[idx]
                S = multiply(bus_mag[bus-1],Imag)
                phi_diff = subtract((bus_ang[bus-1]),Iang)
                for ang in phi_diff:
                    phi.append(exp(1j*ang))
                phi = array(phi)
                S_ = multiply(S,phi)
                P = real(S_)
                Q = imag(S_)
                Pji.extend(P)
                Qji.extend(Q)
                Sji.extend(S)

        retval = list(itertools.chain(Pij,Pji,Qij,Qji,Sij,Sji,Bus_P,Bus_Q))
        return retval

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

    @property
    def isPaused(self):
        return True if self._modelState == OpalApiPy.MODEL_PAUSED else False
