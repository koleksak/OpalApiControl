import sys
from time import sleep

from simcontrol import SimControl
from ltbsetup import LTBSetup
from simstream import Streaming

import logging
logging.basicConfig(level=logging.INFO)


def run_model(project=None, model=None, raw=None, dyr=None, xls=None, path=None):
    """Run a model in ePHASORsim using RT-LAB APIs"""
    ret = 0
    if (not project) or (not model):
        logging.error('RT-LAB project or model undefined.')
        sys.exit(-1)
    if (not raw) and (not xls) :
        logging.error('PSS/E raw file or ePHASORsim Excel file undefined.')
        sys.exit(-1)
    if not dyr:
        logging.debug('PSS/E dyr file not specified')

    sim = SimControl(project, model, path)

    sim_data = LTBSetup(raw='39b_R1.raw', dyr='39b.dyr', path='C:/RT-LABv11_Workspace_New/IEEE39Acq/simulink',
                       simObject=sim)

    streaming = Streaming(name='sim', server='tcp://127.0.0.1:5678', ltb_data=sim_data)



    streaming.start_dime()

    sim.open()
    sim.load()

    sim_data.get_sysparam()
    sim_data.get_varheader_idxvgs()
    streaming.send_init()
    logging.debug('Varheader, SysParam and Idxvgs sent.')
    sleep(0.5)

    sim.start()
    while True:
        streaming.sync_and_handle()

        t, k, varout = sim.acquire_data()
        if t == -1:  # end of data acquisition
            break
        elif not varout:
            continue
        else:
            streaming.vars_to_modules(t, k, varout)
            if streaming.eventTimes != 0:
                if abs(sim.simulationTime - streaming.eventTimes[0]) >= (0.5 * sim.t_acq):
                    streaming.eventQueue, streaming.eventTimes = sim.send_event_signals(streaming.eventQueue)


    streaming.send_done()
    streaming.exit_dime()


if __name__ == "__main__":
    run_model(project='IEEE39Acq', model='phasor01_IEEE39', raw='39b_R1', dyr='39b', path='C:/RT-LABv11_Workspace_New/')
