import logging
logging.basicConfig(level=logging.INFO)


from OpalApiControl import *

if __name__ == '__main__':
    sim = SimControl('WECC181', 'phasor03_PSSE', 'C:/RT-LABv11_Workspace_New/WECC181/models')
    setup = LTBSetup(raw='Curent02_final_ConstZ.raw', dyr='Curent02_final.dyr', path='C:/RT-LABv11_Workspace_New/WECC181/models',
                       simObject=sim)
    setup.get_sysparam()
    print "SysParDone"