"""Extracts Bus Coordinate Data from a Bus data file in ePHASORsim project workspace.
Bus data is then written to a new  (Name)Coords.raw file for the model to be parsed for SysParam Data.
This file can replace the original raw file if no conflicts arise"""


import logging
import os
import sys


class BusCoords():
    def __init__(self,BusDataFile, raw, project, model, path):
        self.raw = raw
        self.project = project
        self.model = model
        self.path = path
        self.projectpath = os.path.join(path,project)
        self.data_folder = ' '
        try:
            os.path.isdir(os.path.join(self.projectpath,'models'))
        except:
            # check simulink folder
            try:
                os.path.isdir(os.path.join(self.projectpath, 'simulink'))
            except:
                logging.error('<Bus Data File must be in ePHASORsim project folder>')
                sys.exit(-1)
            else:
                self.data_folder = 'simulink'
        else:
            self.data_folder = 'models'

        self.BusDataFile = os.path.join(self.projectpath ,'models', BusDataFile)
        self.Coords = []

    def get_bus_coords(self):
        file = open(self.BusDataFile, 'r')
        for num, line in enumerate(file.readlines()):
            line = line.split('\t')
            line.pop()
            lon = line.pop()
            lat = line.pop()
            coords = [lat,lon]
            self.Coords.append(coords)

    def append_coords_to_raw(self):

        rawfile = os.path.join(self.projectpath, self.data_folder, self.model, self.raw)
        file = open(rawfile, 'r')
        temp = []
        for num, line in enumerate(file.readlines()):
            buses = len(self.Coords)
            if num >= 3 and num < buses + 3:
                lat = self.Coords[num-3][0]
                lon = self.Coords[num-3][1]
                line = line.strip('\n')
                newline = line + ', ' + str(lat) + ', ' + str(lon) + '\n'
                temp.append(newline)
                continue
            temp.append(line)

        newfile = str(self.raw)
        newfile = newfile.split('.')
        newfile = newfile[0] + 'Coords.raw'
        newfile = os.path.join(self.projectpath, self.data_folder,self.model, newfile)
        file = open(newfile, 'w')
        for line in temp:
            file.write(line)



