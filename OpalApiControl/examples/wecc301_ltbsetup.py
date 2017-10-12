import logging
logging.basicConfig(level=logging.INFO)


from OpalApiControl import *

if __name__ == '__main__':
    sim = SimControl('WECC_DBW_RealTime', 'Real_Time', 'C:/RT-LABv11_Workspace_New/WECC200/models')
    setup = LTBSetup(raw='WECC_10%Wind_PSSE_RAW.raw', dyr='WECC_10%Wind_PSSE_DYR.dyr', model= 'WECC_DBW_RT',
                     path='C:/RT-LABv11_Workspace_New/WECC200/models',simObject=sim)
    setup.get_sysparam()
    print "SysParDone"