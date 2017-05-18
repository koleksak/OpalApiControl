"""
VarIDX for LTB PSAT Formatted Data Streaming from ePhasorsim Models

"""

import psse32

BusIDX = {}
SynIDX = {}
ExcIDX = {}
LineIDX = {}
TgIDX = {}
HvdcIDX = {}




def set_idxvgs(SysParam):
    """Parses OPAL-RT acquisition formats for groups based on PowerFlow Conditions(buses,syns,loads,etc)
    for IDX LTB streaming"""
    SysParam['Bus']
    nBus = len((SysParam['Bus']))
    print('# of Bus Devices', nBus)
    BusIDX['V'] = list(range(1, nBus+1, 1))
    BusIDX['theta'] = list(range(nBus+1, nBus*2+2, 1))
    BusIDX['P'] = list(range(nBus*2+2, nBus*2+nBus+2, 1))
    BusIDX['Q'] = list(range(nBus*3+2, nBus*3+nBus+2, 1))
    BusIDX['w_Busfreq'] = nBus * 4 + 2
    #Check IDX
    for key in BusIDX.keys():
        print('Bus {} IDX : {}'.format(key, BusIDX[key]))
    # Start Next Index after Last Bus index
    startidx = nBus * 4 + 2
    nSyn = len(SysParam['Syn'])
    print('# of Syn Devices', nSyn)
    SynIDX['p'] = list(range(startidx, startidx+nSyn, 1))
    SynIDX['q'] = list(range(startidx+nSyn, startidx+(nSyn*2)+1, 1))
    SynIDX['delta'] = list(range(startidx+(nSyn*2)+1, startidx+(nSyn*3)+1, 1))
    SynIDX['omega'] = list(range(startidx+(nSyn*3)+1, startidx+(nSyn*4)+1, 1))
    ExcIDX['vf'] = list(range(startidx+(nSyn*4)+1, startidx+(nSyn*5)+1, 1))
    ExcIDX['vm'] = list(range(startidx+(nSyn*5)+1, startidx+(nSyn*6)+1, 1))

    for key in SynIDX.keys():
        print('Syn {} IDX : {}'.format(key,SynIDX[key]))

    for key in ExcIDX.keys():
        print('Exc {} IDX : {}'.format(key,ExcIDX[key]))
    #Start Next Index after Last EXC index
    startidx = startidx+(nSyn*6)+1
    nLine = len(SysParam['Line'])
    print('# of Lines Devices', nLine)

    LineIDX['Pij'] = list(range(startidx, startidx+nLine, 1))
    LineIDX['Pji'] = list(range(startidx+nLine, startidx+(nLine*2)+1, 1))
    LineIDX['Qij'] = list(range(startidx+(nLine*2)+1, startidx+(nLine*3)+1, 1))
    LineIDX['Qji'] = list(range(startidx+(nLine*3)+1, startidx+(nLine*4)+1, 1))
    LineIDX['Iij'] = list(range(startidx+(nLine*4)+1, startidx+(nLine*5)+1, 1))
    LineIDX['Iji'] = list(range(startidx+(nLine*5)+1, startidx+(nLine*6)+1, 1))
    LineIDX['Sij'] = list(range(startidx+(nLine*6)+1, startidx+(nLine*7)+1, 1))
    LineIDX['Sji'] = list(range(startidx+(nLine*7)+1, startidx+(nLine*8)+1, 1))

    for key in LineIDX.keys():
        print('Line{} IDX : {}'.format(key, LineIDX[key]))

    #Start Next Index after Last Lineindex
    startidx = startidx+(nLine*8)+1

    #Gov IDX is last  (TEMP IDX for GOVS)
    nTg = len(SysParam['Tg'])
    print('# of Gov Devices', nTg)

    TgIDX['pm'] = list(range(startidx, startidx+nTg, 1))
    TgIDX['wref'] = list(range(startidx+nTg, startidx+(nTg*2)+1, 1))

    # Start Next Index after Last Tg index+ 1
    startidx = startidx + (nLine * 8) + 1
    for key in TgIDX.keys():
        print('Tg{} IDX : {}'.format(key, TgIDX[key]))
    #ADD WIND MODELS if nec
