from run import run_model
import logging

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    run_model(project='IEEE39Acq', model='phasor01_IEEE39', raw='39b_R1.raw', dyr='39b.dyr',
              path='C:/RT-LABv11_Workspace_New/', server='tcp://127.0.0.1:5678')
