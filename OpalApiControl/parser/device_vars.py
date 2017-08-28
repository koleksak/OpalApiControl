"""Parses FMU package devices for ePHASORsim models. Device variables are retrieved from
each FMU device, and the opal pin I/0 excel file is created to allow for data extraction. Devices locations and
names must then by matched to respective variable pins after Sys Params is Created(SysParams has device info)"""

import logging
import os
import glob

from settings import Settings

class DeviceModels():
    """Devices for use in ePHASORsim models"""
    def __init__(self, project, model, path, SysParam):
        self.SysParam = SysParam
        self.Devices = {}
        self.DevNames = []

    def parse_opal_files(self,path):
        """Parses Individual opal files in FMU path for device model variables"""

        for root, dirs, files in os.walk(path):
            for dev_folder in dirs:
                opalFile = os.path.join(root,dev_folder, 'win_.opal')
                if os.path.exists(opalFile):
                    file = open(opalFile, 'r')
                    for num, line in enumerate(file.readlines()):
                        line = line.strip(' ')
                        line = line.strip('\r\n')
                        try:
                            line = line.split('=')
                        except:
                            #skip all lines without equal signs
                            continue
                        else:
                            if line[0] == 'compName':
                                self.Devices[line[1]] = {}
                                self.DevNames.append(line[1])
                                self.Devices[line[1]]['Vars'] = []
                            if line[0] == 'name':
                                self.Devices[self.DevNames[-1]]['Vars'].append(line[1])
                else:
                    logging.log(1,'No win_.opal file found in {}'.format(dev_folder))
                    continue

    def set_devices_to_buses(self):
        """Searches SysParams for the bus ID containing the Device with its associated subdevices"""