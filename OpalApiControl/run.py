import sys
import os
from time import sleep

from simcontrol import SimControl
from ltbsetup import LTBSetup
from streaming import Streaming

from consts import  *

import logging


def run_model(project=None, model=None, raw=None, dyr=None, xls=None, path=None, server='tcp://127.0.0.1:5678'):
    """Run a model in ePHASORsim using RT-LAB APIs"""
    ret = 0
    if (not project) or (not model):
        logging.error('RT-LAB project or model undefined.')
        sys.exit(-1)
    if (not raw) and (not xls):
        logging.error('PSS/E raw file or ePHASORsim Excel file undefined.')
        sys.exit(-1)
    if not dyr:
        logging.debug('PSS/E dyr file not specified')

    sim = SimControl(project, model, path)

    simulink = os.path.join(path,project, 'simulink')
    models = os.path.join(path,project, 'models')
    if not os.path.isdir(simulink):
        logging.error('No <{}> directory found.'.format(simulink))
        if not os.path.isdir(models):
            logging.error('No <{}> directory found.'.format(models))
            sys.exit(1)
        else:
            logging.info('Using <{}> directory'.format(models))
            modelPath = models
    else:
        logging.info('Using <{}> directory'.format(simulink))
        modelPath = simulink


    sim_data = LTBSetup(raw=raw, dyr=dyr, xls=xls, path=modelPath, model=model, simObject=sim)

    streaming = Streaming(name='sim', server=server, ltb_data=sim_data)

    sim.open()
    sim.load()

    sim_data.get_sysparam()
    sim_data.get_varheader_idxvgs()
    sim.set_settings(sim_data.Settings)
    streaming.send_init()
    logging.debug('Varheader, SysParam and Idxvgs sent.')
    sleep(0.5)

    sim.start()

    streaming.run()
