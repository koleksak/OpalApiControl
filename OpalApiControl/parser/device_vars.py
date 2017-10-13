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
        self.KeepVars = {'GENCLS': ['ANGLE', 'SLIP','P_gen', 'Q_gen','Psup', 'Qsup'],
               'GENROU': ['ANGLE', 'P_gen', 'Q_gen', 'SLIP', 'Ed_p', 'Eq_p', 'PSI1_d', 'PSI2_q'],
               }
        self.KeepVarsOrdered = defaultdict(list)
        self.SynePHASOR_out_ports = ['ANGLE','SLIP','P_gen', 'Q_gen', 'Ed_p','Eq_p', 'PSI1_d', 'PSI2_q']
        self.SynePHASOR_in_ports = ['Psup', 'Qsup']
        self.gen_list = []
        self.busePHASOR_in_ports = ['active3PGFault', 'status']

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

    def create_excel_file_pins_vars(self):
        """Creates excel pin rows for each var and its respective bus locations."""

        fileout = self.filepath + 'pins.xlsx'
        pins_sheet = self.ExcelPins.active
        pins_sheet.title = 'Pins'

        for bus in sorted(self.BusVars):
            for idx in self.BusVars[bus]:
                for id in idx.keys():
                    self.gen_list.append('gen_' + str(bus) + '_' + str(id) + '/')
                    for var in idx[id]:
                        var_avail = var.split('.')
                        var_class = var_avail[0]
                        var_name = var_avail[-1]
                        for var_check in self.KeepVars.keys():
                            if var_class.find(var_check.lower()) != -1 and var_name in self.KeepVars[var_check]:
                                cell = self.gen_list[-1] + var
                                self.KeepVarsOrdered[var_name].append(cell)
                            else:
                                continue

        for var in self.SynePHASOR_out_ports:
            row_init = []
            row_data = ['outgoing', var]
            row_data.extend(self.KeepVarsOrdered[var])
            row_init.extend(row_data)
            # row_init.append(var)
            # row_init.extend(self.KeepVarsOrdered[var])
            self.ExcelTemp.append(row_init)
            pins_sheet.append(row_init)

        pins_sheet.append(self.add_var_to_excel_by_bus('Vmag','outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_bus('Vang','outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_branch('LinesIj_Imag', 0, 'outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_branch('LinesJi_Imag', 1, 'outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_branch('LinesIj_Iang', 2, 'outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_branch('LinesJi_Iang', 3, 'outgoing'))
        pins_sheet.append(self.add_var_to_excel_by_bus('active3PGFault', 'incoming'))
        pins_sheet.append(self.add_var_to_excel_by_gen('Psup', 'incoming'))
        pins_sheet.append(self.add_var_to_excel_by_gen('Qsup', 'incoming'))
        pins_sheet.append(self.add_var_to_excel_by_gen('TRIP','incoming'))
        pins_sheet.append(self.add_var_to_excel_by_load('status', 'incoming','P'))
        pins_sheet.append(self.add_var_to_excel_by_load('status', 'incoming','Q'))
        pins_sheet.append(self.add_var_to_excel_by_branch('status', 4, 'incoming'))
        pins_sheet.append(self.add_var_to_excel_by_branch('status', 5, 'incoming'))




        self.ExcelPins.save(filename=fileout)

    def gen_port_helper(self):
        """helps generate excel file ins/outs for generator variables"""
        pass

    def add_var_to_excel_by_bus(self, var,i_o):
        var_init = []
        row_init = []
        for bus in range(0, len(self.SysParam['Bus'])):
            var_init.append('bus_' + str(bus + 1) + '/' + str(var))
        row_data = [str(i_o), str(var)]
        row_data.extend(var_init)
        row_init.extend(row_data)
        # row_init.append(str(var))
        # row_init.extend(var_init)
        return row_init

    def add_var_to_excel_by_gen(self, var,i_o):
        var_init = []
        row_init = []
        for gen in self.gen_list:
            var_init.append(gen + str(var))
        row_data = [str(i_o), str(var)]
        row_data.extend(var_init)
        row_init.extend(row_data)
        # row_init.append(str(var))
        # row_init.extend(var_init)
        return row_init

    def add_var_to_excel_by_load(self, var,i_o, type):
        var_init = []
        row_init = []
        for bus in range(0, len(self.SysParam['Bus'])):
            var_init.append('load_' + str(type) + '_' + str(bus + 1) + '_BL/' + str(var))
        row_data = [str(i_o), str(var)]
        row_data.extend(var_init)
        row_init.extend(row_data)
        # row_init.append(str(var))
        # row_init.extend(var_init)
        return row_init

    def add_var_to_excel_by_branch(self, var, order, i_o):
        var_init = []
        row_init = []
        if order == 0:
            for lines in self.Settings.Lineij:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/Imag0')
        elif order == 1:
            for lines in self.Settings.Lineij:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/Imag1')
        elif order == 2:
            for lines in self.Settings.Lineij:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/Iang0')
        elif order == 3:
            for lines in self.Settings.Lineij:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/Iang1')
        elif order == 4:
            for lines in self.Settings.Lineij:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/' + str(var))
        elif order == 5:
            for lines in self.Settings.Lineji:
                var_init.append('line_' + str(lines[0]) + '_to_' + str(lines[1]) + '_' + str(lines[2]) + '/' + str(var))
        else:
            logging.warning('<Unknown branch to-from given. No Branch data added>')
            return 0
        row_data = [str(i_o), str(var)]
        row_data.extend(var_init)
        row_init.extend(row_data)
        # row_init.append(str(var))
        # row_init.extend(var_init)
        return row_init

    def create_excel_file_pins_bus(self): #TODO: arrange in order by var. Must be done for ports to match var list in SysPar
        """Creates excel pin rows for each bus and all of the variables associated with the device group"""

        fileout = self.filepath + 'pins.xlsx'
        pins_sheet = self.ExcelPins.active
        pins_sheet.title = 'Pins'

        for bus in sorted(self.BusVars):
            for idx in self.BusVars[bus]:
                for id in idx.keys():
                    tmprow = []
                    row_init = []
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
                    row_data = ['outgoing','Gen_' + str(bus) + '_Vars']
                    row_data.extend(tmprow)
                    row_init.extend(row_data)
                    # row_init.append( 'Gen_' + str(bus) + '_Vars')
                    # row_init.extend(tmprow)
                    self.ExcelTemp.append(tmprow)
                    pins_sheet.append(row_init)

        self.ExcelPins.save(filename=fileout)



