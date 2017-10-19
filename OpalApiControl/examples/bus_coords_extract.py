import logging
logging.basicConfig(level=logging.INFO)


from OpalApiControl import *
from OpalApiControl.parser.bus_coords import BusCoords
if __name__ == '__main__':
    coords = BusCoords('WECCBusDataNoWind.txt', 'Curent02_final_ConstZ.raw', 'WECC_Wind_Inertia_Siqi', 'phasor03_PSSE', 'C:/RT-LABv11_Workspace_New/')
    coords.get_bus_coords()
    coords.append_coords_to_raw()