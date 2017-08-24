import logging
logging.basicConfig(level=logging.INFO)


from OpalApiControl import *

if __name__ == '__main__':
    sim = SimControl('IEEE39Acq', 'phasor01_IEEE39', 'C:/RT-LABv11_Workspace_New/IEEE39Acq/simulink')
    setup = LTBSetup(raw='39b_R1.raw', dyr='39b.dyr', path='C:/RT-LABv11_Workspace_New/IEEE39Acq/simulink',
                       simObject=sim)
    setup.get_sysparam()
    print "SysParDone"