"""Parses FMU package devices for ePHASORsim models. Device variables are retrieved from
each FMU device, and the opal pin I/0 excel file is created to allow for data extraction. Devices locations and
names must then by matched to respective variable pins after Sys Params is Created(SysParams has device info)"""

import logging
import os
import glob
from openpyxl import Workbook
from openpyxl import load_workbook
from collections import defaultdict
from collections import OrderedDict
import itertools

from settings import Settings

class DeviceModels():
    """Devices for use in ePHASORsim models"""
    def __init__(self, project, model, path, Settings):
        self.filepath = path
        self.Settings = Settings
        self.SysParam = Settings.SysParam
        self.Devices = {}
        self.DevNames = []
        self.DevicesAtBus = Settings.DevicesAtBus
        self.DevicePins = defaultdict(OrderedDict)
        self.BusVars = defaultdict(list)
        self.DeviceGroup = {}
        self.DeviceGroupCount = {}      #Counts the occurences of each Device Group
        self.ExcelPins = Workbook()
        self.ExcelTemp = []
        self.KeepVars = {'GENCLS': ['ANGLE', 'SLIP',],
               'GENROU': ['ANGLE', 'SLIP', 'Ed_p', 'Eq_p', 'PSI1_d', 'PSI2_q'],
               }

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

    def find_devices_at_bus(self):
        """Used to test excel row, col creation process for devices(Generator Devices)"""

        for bus in self.Settings.Syn:
            busidx = bus[0]
            tempDevs = defaultdict(list)
            for device, params in self.DevicesAtBus.iteritems():
                #TODO: Create row and col mock excel sheet for each bus, and the devices/ids to go with it
                for bus_info in params:
                    if bus_info['Bus'] == busidx:
                        tempDevs[bus_info['Id']].append(device)
                    self.DevicePins[busidx].update(tempDevs)


    def find_device_vars(self):
        """Finds the correct variable list for the device at bus# depending on device configuration"""
        for bus in self.DevicePins.keys():
            for id, devices in self.DevicePins[bus].iteritems():
                for dev in itertools.permutations(devices):
                    dev_find = '_'.join(dev)
                    dev_find = dev_find.upper()
                    if dev_find in self.DevNames:
                        self.BusVars[bus].append({id : self.Devices[dev_find]['Vars']})
                        if dev_find in self.DeviceGroupCount.keys():
                            self.DeviceGroupCount[dev_find] += 1
                        else:
                            self.DeviceGroupCount[dev_find] = 1
                        self.DeviceGroup[bus] = dev_find #Updates Devices to the proper order and naming of FMU
                        break


    def arrange_bus_pins_by_var(self):
        """Creates excel pin rows for each variable for a device group and each bus containing the device"""
        pass


    def create_excel_file_pins(self):
        """Creates excel pin rows for each bus and all of the variables associated with the device group"""

        fileout = self.filepath + 'pins.xlsx'
        pins_sheet = self.ExcelPins.active
        pins_sheet.title = 'Pins'

        for bus in self.BusVars.keys():
            for idx in self.BusVars[bus]:
                for id in idx.keys():
                    tmprow = []
                    celltemp = 'gen_' + str(bus) + '_' + str(id) + '/'
                    for var in idx[id]:
                        var_avail = var.split('.')
                        var_class = var_avail[0]
                        var_name = var_avail[-1]
                        for var_check in self.KeepVars.keys():
                            if var_class.find(var_check.lower()) != -1 and var_name in self.KeepVars[var_check]:
                                cell = celltemp + var
                                tmprow.append(cell)
                            else:
                                continue
                    self.ExcelTemp.append(tmprow)
                    pins_sheet.append(tmprow)


        # for cell_row in range(1, rows):
        #         pins_sheet.append([self.ExcelPins[cell_row]])

        self.ExcelPins.save(filename=fileout)



