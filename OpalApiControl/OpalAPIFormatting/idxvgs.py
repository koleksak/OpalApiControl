"""
VarIDX for LTB PSAT Formatted Data Streaming from ePhasorsim Models

"""

import psse32
import dime
import stream

Idx = {}
BusIDX = {}
SynIDX = {}
ExcIDX = {}
LineIDX = {}
TgIDX = {}
HvdcIDX = {}
Varheader = []
var_keys_order = ['V', 'theta', 'P', 'Q', 'w_Busfreq', 'p', 'q', 'delta', 'omega',
                  'vf', 'vm', 'Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji',
                  'pm', 'wref']
idx_vgs_order = ['Bus', 'Syn', 'Exc', 'Line', 'Tg']

def set_idxvgs(SysParam):
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
        print('Line{} IDX : {}'.format(key, LineIDX[key]))
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


def set_varheader():
    """Creates Variable Names for varidx indices"""

    for device in idx_vgs_order:
        for var in var_keys_order:
            if var in Idx[device].keys():
                for i in range(1, len(Idx[device][var])+1):
                    Varheader.append(var+'_'+str(i))


def check_set_varheader():
    print Varheader

def var_idx_vgs_list():
    for count in range(0, len(Varheader)):
        print('Var: {}  Idx: {} '.format(Varheader[count], count+1))

def send_varhead_idxvgs():
    """Sends Varheader and Indices to Dime server after power flow"""

    stream.dimec.broadcast('Varheader')
    stream.dimec.broadcast('Idx')
