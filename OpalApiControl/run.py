import sys
import os
from time import sleep

from simcontrol import SimControl
from ltbsetup import LTBSetup
from streaming import Streaming

from consts import  *

import logging


def run_model(project=None, model=None, raw=None, dyr=None, xls=None, path=None,server='tcp://127.0.0.1:5678',add_power_devs=None,pills=None):
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

    sim = SimControl(project, model, path,pills=pills)

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

    streaming = Streaming(name='sim', server=server, ltb_data=sim_data,pills=pills)

    sim.open()
    sim.load()
    streaming._pills['loaded'].acquire()
    streaming._pills['loaded'].notifyAll()
    logging.debug("<loading done... notifying waiters>")
    streaming._pills['loaded'].release()

    sim_data.get_sysparam()
    sim.set_settings(sim_data.Settings)
    sim_data.get_varheader_idxvgs(add_power_devs)
    streaming.send_init()
    logging.debug('Varheader, SysParam and Idxvgs sent.')
    sleep(2)

    while not streaming._pills['end'].isSet():
        with streaming._pills['condition']:
            logging.info("<waiting to start>")
            if not streaming._pills['stop'].isSet():
                streaming._pills['condition'].wait()
                logging.debug("Condition set. Starting run sequence")

                if streaming._pills['start'].isSet() and not streaming._pills['resume'].isSet():
                    sim.start()
                elif streaming._pills['start'].isSet() and streaming._pills['resume'].isSet():
                    sim.resume()
                streaming.run()

            else:
                sim.stop()
                break

