"""
VarIDX for LTB PSAT Formatted Data Streaming from ePhasorsim Models

"""

import json
from OpalApiControl.signals import signalcontrol
from numpy import array, ndarray


Idx = {}
Idxvgs = {}
BusIDX = {}
SynIDX = {}
ExcIDX = {}
LineIDX = {}
TgIDX = {}
HvdcIDX = {}
global Varheader
Varheader = []
#var_keys_order = ['w_Busfreq', 'delta', 'omega','pm', 'wref', 'vf', 'vm',
#    'theta', 'V', 'P', 'Q', 'p', 'q', 'Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji']
idx_vgs_order = ['Bus', 'Syn', 'Exc', 'Line', 'Tg']
#Generate state and alg order lists from ePhasorsim signalnames for linked association
state = []
alg = []
state_order = ['w_Busfreq', 'delta', 'omega', 'pm', 'wref', 'vf', 'vm']
alg_order = ['theta', 'V', 'P', 'Q', 'p', 'q', 'Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji']
BusPar = ['V', 'theta', 'P', 'Q', 'w_Busfreq']
SynPar = ['p', 'q', 'delta', 'omega']
ExcPar = ['vf', 'vm']
LinePar = ['Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji']
TgPar = ['pm', 'wref']
SysPar = {
    'Bus': ['V', 'theta', 'P', 'Q', 'w_Busfreq'],
    'Syn': ['p', 'q', 'delta', 'omega'],
    'Exc': ['vf', 'vm'],
    'Line': ['Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji'],
    'Tg': ['pm', 'wref']}


def set_ephasor_ports(project, model):
    """sets the order for IDXvgs and Varheader based upon the solver output ports in ePhasorsim"""
    item = 0
    Varheader = signalcontrol.acquisitionSignalsParse(project, model)
    varhead = []
    for var in Varheader:
        var = var.split('(')
        varhead.append(var[0])

    Idxvgs = dict()

    # for dev, vars in SysPar.items():
    #     f
    for idx, item in enumerate(varhead):
        indexed = False
        matlab_idx = idx + 1

        for dev, vars in SysPar.items():
            if item in vars:
                if dev not in Idxvgs.keys():
                    Idxvgs[dev] = dict()

                if dev in Idxvgs.keys() and (item not in Idxvgs[dev].keys()):
                    Idxvgs[dev][item] = []

                if dev in Idxvgs.keys() and item in Idxvgs[dev].keys():
                    Idxvgs[dev][item].append(matlab_idx)
                    indexed = True
                    break
        if not indexed:
            print('Warning: Variable <{}> not added to Idxvgs.'.format(item))

    # Convert to numpy column arrays
    for dev in Idxvgs.keys():
        for var, val in Idxvgs[dev].items():
            Idxvgs[dev][var] = array(val).T

    return Idxvgs, Varheader


def set_varheader():
    """Creates Variable Names for varidx indices"""
    #print('Idxvgs', Idxvgs)
    for device in idx_vgs_order:
        for var in state_order:
            if var in Idxvgs[device].keys():
                for i in range(1, len(Idxvgs[device][var])+1):
                    Varheader.append(var+'_'+str(i))

    for device in idx_vgs_order:
        for var in alg_order:
            if var in Idxvgs[device].keys():
                for i in range(1, len(Idxvgs[device][var])+1):
                    Varheader.append(var+'_'+str(i))
    return Varheader


def send_varhead_idxvgs(dev, dimec, Varheader):
    """Sends Varheader and Indices to Dime server after power flow"""
    JsonVarheader = json.dumps(Varheader)
    JsonIdx = json.dumps(Idx)
    dimec.send_var(dev, 'sim', JsonVarheader)
    dimec.send_var(dev, 'sim', JsonIdx)
