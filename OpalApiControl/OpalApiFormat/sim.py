"""Streaming data thread for ePhasorsim using OpalApi Interface"""

from OpalApiControl.OpalApiFormat import stream
from OpalApiControl.OpalApiFormat import psse32
from OpalApiControl.OpalApiFormat import psse320
import threading
from time import sleep
import OpalApiPy
from system import acquire

#if __name__ == "__main__":
#def simulate():
class Simulate(threading.Thread):
    def __init__(self, Control, project, model, rawfile, dyrfile):
        threading.Thread.__init__(self)
        #self.SimNum = SimNum
        self._Control = Control
        sim_stop = threading.Event()
        #Control for pausing model
        self.sim_stop = sim_stop
        self.project = project
        self.model = model
        self.rawfile = rawfile
        self.dyrfile = dyrfile
        SysParam, Varheader, Idxvgs, project, model = psse32.init_pf_to_stream(self.project, self.model, self.rawfile, self.dyrfile)
        # SysParam, Varheader, Idxvgs, project, model = psse32.init_pf_to_stream()
        self.SysParam = SysParam
        self.Varheader = Varheader
        self.Idxvgs = Idxvgs
        self.project = project
        self.model = model
        #acq_wait = threading.Event()
        #self.acq_wait = acq_wait

    def run(self):
        self.sim_stop.set()
        stream.ltb_stream_sim(self.SysParam,  self.Varheader, self.Idxvgs, self.project,
                              self.model, self.sim_stop)
        print"Simulation Successful"




if __name__ == "__main__":
    # simu = Simulate(True, 'IEEE118', 'phasor06_IEEE118', 'ieee118b', 'ieee118b')
    simu = Simulate(True, 'IEEE39Acq', 'phasor01_IEEE39', '39b_R1', '39b')
    simu.start()
    #sleep(3)
    # exec (open('C:/Users/opalrt/repos/OpalApiControl/OpalApiControl/se_examp.py').read())
    while(simu.is_alive()):
        pass

