"""Initialization class for System Parameters, Idxvgs, and Varheader to be sent to LTB.
Idxvgs, and varheader are created from ePHASORsim output signal ports"""


import os

from simcontrol import SimControl
from OpalApiFormat import psse32_new_clean

import logging
logging.basicConfig(level=logging.INFO)


class LTBSetup(object):
    """Class for parsing files and create SysParam data for LTB streaming"""
    def __init__(self, raw='', dyr='', xls='', path='', simObject=None):
        assert raw or xls
        self.raw = raw
        self.xls = xls
        self.dyr = dyr
        self.sim = simObject

        self._rawPath = os.path.join(path, raw)
        self._xlsPath = os.path.join(path, xls)
        self._dyrPath = os.path.join(path, dyr)

        self.SysParam = None
        self.Varheader = None
        self.Idxvgs =None

    def get_varheader_idxvgs(self):
        if not self.sim:
            logging.error('Pass SimControl object to LTBData to get Varheader and Idxvgs.')
        self.Varheader, self.Idxvgs = self.sim.varheader_idxvgs()

    def get_sysparam(self):
        self.SysParam = psse32_new_clean.init_pf_to_stream(self._rawPath, self._dyrPath)

if __name__ == '__main__':
    sim = SimControl('IEEE39Acq', 'phasor01_IEEE39', 'C:/RT-LABv11_Workspace_New/IEEE39Acq/simulink')
    setup = LTBSetup(raw='39b_R1.raw', dyr='39b.dyr', path='C:/RT-LABv11_Workspace_New/IEEE39Acq/simulink',
                       simObject=sim)
    setup.get_sysparam()
    print "SysParDone"