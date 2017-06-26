"""
VarIDX for LTB PSAT Formatted Data Streaming from ePhasorsim Models

"""
import os
import psse32
import dime
import stream
import json
from OpalApiControl.signals import signalcontrol


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
state_order = ['w_Busfreq', 'delta', 'omega','pm', 'wref', 'vf', 'vm']
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

def set_idxvgs_gen_helper(SysParam):
    """Generates IDX matrix with elements to ease Idxvgs creation. Follows Variable name orders
    defined in (Device)Par lists."""

    nBus = len((SysParam['Bus']))
    for item in BusPar:
        BusIDX[item] = range(0, nBus, 1)
    Idx['Bus'] = BusIDX

    nSyn = len(SysParam['Syn'])
    for item in SynPar:
        SynIDX[item] = range(0, nSyn, 1)
    Idx['Syn'] = SynIDX

    for item in ExcPar:
        ExcIDX[item] = range(0, nSyn, 1)
    Idx['Exc'] = ExcIDX

    nLine = len(SysParam['Line'])
    for item in LinePar:
        LineIDX[item] = range(0, nLine, 1)
    Idx['Line'] = LineIDX

    nTg = len(SysParam['Tg'])
    for item in TgPar:
        TgIDX[item] = range(0, nTg, 1)
    Idx['Tg'] = TgIDX

    #ADD WIND MODELS if nec


def set_ephasor_ports(project, model):
    """sets the order for IDXvgs and Varheader based upon the solver output ports in ePhasorsim"""
    #Idx = {}
    item = 0
    idx_list = []
    Varheader = signalcontrol.acquisitionSignalsParse(project, model)
    varhead = []
    for var in Varheader:
        var = var.split('(')
        varhead.append(var[0])


    while item < len(varhead):
        varname = varhead[item]
        for param in SysPar.keys():
            param_list = SysPar[param]
            if param in Idx.keys():
                idx_list = []
                pass
            else:
                Idx[param] = {}
                idx_list = []

            #print SysPar[param]
            if varname in SysPar[param] and item != len(varhead):
                #idxvgs[param][varname] = {}
                #print('Varheadit:{}  Var:{} '.format(varhead[item], var))
                prevname = varname
                currentname = varname
                while prevname == currentname and item != len(varhead):
                    idx_list.append(item+1)
                    Idx[param][varname] = idx_list
                    try:
                        currentname = varhead[item+1]
                    except:
                        pass
                    item += 1

    return Idx, Varheader


def set_idxvgs(SysParam):  ###REPLACED WITH set_idx_gen_helper()
    """Parses OPAL-RT acquisition formats for groups based on PowerFlow Conditions(buses,syns,loads,etc)
    for IDX LTB streaming"""

    nBus = len((SysParam['Bus']))
    print('# of Bus Devices', nBus)
    BusIDX['V'] = list(range(1, nBus+1, 1))
    BusIDX['theta'] = list(range(nBus+1, nBus*2+1, 1))
    BusIDX['P'] = list(range(nBus*2+1, nBus*2+nBus+1, 1))
    BusIDX['Q'] = list(range(nBus*3+1, nBus*3+nBus+1, 1))
    BusIDX['w_Busfreq'] = list(range(nBus*4+1, nBus*5 + 1, 1))
    Idx['Bus'] = BusIDX


    #Check IDX
    for key in BusIDX.keys():
        print('Bus {} IDX : {}'.format(key, BusIDX[key]))
        print('Length: ', len(BusIDX[key]))
    # Start Next Index after Last Bus index
    startidx = nBus*5 + 1
    nSyn = len(SysParam['Syn'])
    print('# of Syn Devices', nSyn)
    SynIDX['p'] = list(range(startidx, startidx+nSyn, 1))
    SynIDX['q'] = list(range(startidx+nSyn, startidx+(nSyn*2), 1))
    SynIDX['delta'] = list(range(startidx+(nSyn*2), startidx+(nSyn*3), 1))
    SynIDX['omega'] = list(range(startidx+(nSyn*3), startidx+(nSyn*4), 1))
    ExcIDX['vf'] = list(range(startidx+(nSyn*4), startidx+(nSyn*5), 1))
    ExcIDX['vm'] = list(range(startidx+(nSyn*5), startidx+(nSyn*6), 1))
    Idx['Syn'] = SynIDX
    Idx['Exc'] = ExcIDX

    for key in SynIDX.keys():
        print('Syn {} IDX : {}'.format(key, SynIDX[key]))
        print('Length: ', len(SynIDX[key]))

    for key in ExcIDX.keys():
        print('Exc {} IDX : {}'.format(key, ExcIDX[key]))
    #Start Next Index after Last EXC index
    startidx = startidx+(nSyn*6)
    nLine = len(SysParam['Line'])
    print('# of Lines Devices', nLine)

    LineIDX['Pij'] = list(range(startidx, startidx+nLine, 1))
    LineIDX['Pji'] = list(range(startidx+nLine, startidx+(nLine*2), 1))
    LineIDX['Qij'] = list(range(startidx+(nLine*2), startidx+(nLine*3), 1))
    LineIDX['Qji'] = list(range(startidx+(nLine*3), startidx+(nLine*4), 1))
    LineIDX['Iij'] = list(range(startidx+(nLine*4), startidx+(nLine*5), 1))
    LineIDX['Iji'] = list(range(startidx+(nLine*5), startidx+(nLine*6), 1))
    LineIDX['Sij'] = list(range(startidx+(nLine*6), startidx+(nLine*7), 1))
    LineIDX['Sji'] = list(range(startidx+(nLine*7), startidx+(nLine*8), 1))
    Idx['Line'] = LineIDX

    for key in LineIDX.keys():
        print('Line {} IDX : {}'.format(key, LineIDX[key]))
        print('Length: ', len(LineIDX[key]))
    #Start Next Index after Last Lineindex
    startidx = startidx+(nLine*8)

    #Gov IDX is last  (TEMP IDX for GOVS)
    nTg = len(SysParam['Tg'])
    print('# of Gov Devices', nTg)

    TgIDX['pm'] = list(range(startidx, startidx+nTg, 1))
    TgIDX['wref'] = list(range(startidx+nTg, startidx+(nTg*2), 1))
    Idx['Tg'] = TgIDX

    # Start Next Index after Last Tg index
    for key in TgIDX.keys():
        print('Tg{} IDX : {}'.format(key, TgIDX[key]))
        print('Length: ', len(TgIDX[key]))
    #ADD WIND MODELS if nec


def idx_choose_order():
    """Sets the idxvgs based upon state_order and alg_order defined at top of module"""
    #print('IDX: ', Idx)
    startidx = 0
    endidx = 0
    for device in idx_vgs_order:
        Idxvgs[device] = {}
        #print ('Device', device)
        for var in state_order:
            #print ('Var', var)
            if var in Idx[device].keys():
                endidx += len(Idx[device][var])
                Idxvgs[device][var] = list(range(startidx, endidx, 1))
                startidx = endidx

    for device in idx_vgs_order:
        #print ('Device', device)
        for var in alg_order:
            #print ('Var', var)
            if var in Idx[device].keys():
                endidx += len(Idx[device][var])
                Idxvgs[device][var] = list(range(startidx, endidx, 1))
                startidx = endidx

    return Idxvgs


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


def check_set_varheader():
    print Varheader


def var_idx_vgs_list():
    for count in range(0, len(Varheader)):
        print('Var: {}  Idx: {} '.format(Varheader[count], count+1))


def send_varhead_idxvgs(dev, dimec, Varheader):
    """Sends Varheader and Indices to Dime server after power flow"""
    JsonVarheader = json.dumps(Varheader)
    JsonIdx = json.dumps(Idx)
    dimec.send_var(dev, 'sim', JsonVarheader)
    dimec.send_var(dev, 'sim', JsonIdx)
