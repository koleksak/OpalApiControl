"""Initialization class for System Parameters, Idxvgs, and Varheader to be sent to LTB.
Idxvgs, and varheader are created from ePHASORsim output signal ports"""


import logging
import os
import sys

from OpalApiControl.parser import psse


class LTBSetup(object):
    """Class for parsing files and create SysParam data for LTB streaming"""
    def __init__(self, raw='', dyr='', xls='', path='',model='',simObject=None):
        if not os.path.isdir(path):
            logging.error('Path <{}> does not exist.'.format(path))
            sys.exit(1)

        assert raw or xls
        self.raw = None
        self.xls = None
        self.dyr = None
        self.sim = simObject

        if raw:
            self.raw = os.path.join(path, raw)
            if(os.path.exists(self.raw)):
                pass
            else:
                self.raw = os.path.join(path, model, raw)
        if xls:
            self._xlsPath = os.path.join(path, xls)
        if dyr:
            self.dyr = os.path.join(path, dyr)
            if (os.path.exists(self.dyr)):
                pass
            else:
                self.dyr = os.path.join(path, model, dyr)

        self.Settings = None
        self.SysParam = None
        self.Varheader = None
        self.Idxvgs =None


    def get_varheader_idxvgs(self):
        if not self.sim:
            logging.error('Pass SimControl object to LTBData to get Varheader and Idxvgs.')
        self.Varheader, self.Idxvgs = self.sim.varheader_idxvgs()

    def get_sysparam(self):
        self.Settings = psse.init_pf_to_stream(self.raw, self.dyr)
        self.SysParam = self.Settings.SysParam
        self.SysName = self.Settings.SysName
