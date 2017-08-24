"""SE example for testing ePhasorsim streaming"""

from time import sleep
from dime import dime
from simcontrol import SimControl

dimec = dime.Dime('SE', 'tcp://127.0.0.1:5678')
dimec.start()


SE = {'param': ['Bus', 'Line', 'PV', 'PQ'],
      'vgsvaridx': list(range(0, 10000)),
      'usepmu': 1.,
      'limitsample': 1.,
      }


if __name__ == '__main__':
    sim = SimControl('IEEE39Acq', 'phasor01_IEEE39', 'C:\RT-LABv11_Workspace_New')
    dimec.send_var('sim', 'SE', SE)


    while True:
        vars = dimec.sync()
        if vars:
            mods = dimec.workspace
        sleep(0.01)
    dimec.exit()



