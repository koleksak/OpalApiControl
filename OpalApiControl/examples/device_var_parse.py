import logging
logging.basicConfig(level=logging.INFO)
import os

from OpalApiControl.parser.device_vars import DeviceModels
from OpalApiControl.parser import psse

if __name__ == '__main__':
    path = '/Users/Kellen/Documents/UT/CURENT/WECC181/models/phasor03_PSSE'
    rawfile = os.path.join(path, 'Curent02_final_ConstZ.raw')
    dyrfile = os.path.join(path, 'Curent02_final.dyr')
    SysParam = psse.init_pf_to_stream(rawfile, dyrfile)
    fmu_path = os.path.join(path, 'FMU')
    devices = DeviceModels('WECC181', 'phasor03_PSSE', fmu_path, SysParam)
    #opalfile = os.path.join(fmu_path,'GENCLS/win_.opal')
    devices.parse_opal_files(fmu_path)
    print 'devices added'