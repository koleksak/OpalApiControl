"""
VarIDX and VARVGS for LTB PSAT Formatted Data Streaming from ePhasorsim Running Models

"""

import OpalApiPy

import acquisitioncontrol
from OpalApiControl.system import acquire
from OpalApiControl.OpalAPIFormatting import psse32

Bus_Data = acquisitioncontrol.DataList(1)
BusIDX = {}
busvolt = []
busang = []
Syn_Data = acquisitioncontrol.DataList(2)
SynIDX = {}
synang = []
synspeed = []
syne1d = []
syne1q = []
syne2d = []
syne2q = []
synpsid = []
synpsiq = []
synact = []
synreact = []
ExcIDX = {}
excVref = []
excVmag = []

Load_Data = acquisitioncontrol.DataList(3)


def stream_data(groups):
    """Creates Bus,Generator, and Load Data Structure as well as the acquisition threads for dynamic streaming. Threads run
     until the model is paused, then must be run again if further acquisition is required.  Data Lists will be appended to
     granted the Bus_Data, etc, if this module is imported

     groups = (group# tuple, in ascending order)"""
    if 1 in groups:
        bus_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Bus_Data, groups[0],
                                                       "Bus Data Thread Set", 1)
    if 2 in groups:
        syn_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Syn_Data, groups[1],
                                                       "Generator Data Thread Set", 1)
    if 3 in groups:
        load_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Load_Data, groups[2],
                                                       "Load Data Thread Set", 1)
    if 4 in groups:
        line_set = acquisitioncontrol.StartAcquisitionThread('ephasorFormat1', 'phasor01_IEEE39', Load_Data, groups[3],
                                                         "Load Data Thread Set", 1)
    if 1 in groups:
        bus_set.start()
    if 2 in groups:
        syn_set.start()
    if 3 in groups:
        load_set.start()
    #if 4 in groups:
    #    line_set.start()
    acquire.connectToModel('ephasorFormat1','phasor01_IEEE39')
    OpalApiPy.SetAcqBlockLastVal(0,1)



def stream_server_data():
    """Sends acquisition data to server. Slight re-ordering is done for Bus P and Q(Must append Syn,Load P and Q)"""
    All_Acq_Data = []
    All_Acq_Data.extend(Bus_Data.returnLastAcq())
    All_Acq_Data.append(psse32.freq)
    All_Acq_Data.extend(Load_Data.returnLastAcq())
    All_Acq_Data.extend(Syn_Data.returnLastAcq())


    return All_Acq_Data


















def parse_stream():
    """Parses OPAL-RT acquisition formats for groups based on PowerFlow Conditions(buses,syns,loads,etc)
    for IDX LTB streaming"""

    for businfo in range(Bus_Data):
        if businfo < len(Bus_Data.dataValues)/2:
            busvolt.append(Bus_Data[businfo])
        else:
            busang.append(Bus_Data[businfo])
    BusIDX['V'] = busvolt
    BusIDX['theta'] = busang
    BusIDX['w_Busfreq'] = psse32.freq
    #ADD P and Q With Gen and Load data
    #BusIDX['P'] = []
    #BusIDX['Q'] = []

    step = 1
    for syninfo in range(Syn_Data):
        if syninfo < len(Syn_Data.dataValues)/6:
            synang.append(Syn_Data[syninfo])
        if (syninfo < len(Syn_Data.dataValues)*2)/6:
            synspeed.append(Syn_Data[syninfo])
        if syninfo < (len(Syn_Data.dataValues)*3)/6:
            excVmag.append(Syn_Data[syninfo])
        if syninfo < (len(Syn_Data.dataValues)*4)/6:
            synact.append(Syn_Data[syninfo])
        if syninfo < (len(Syn_Data.dataValues)*5)/6:
            synreact.append(Syn_Data[syninfo])
        if syninfo < (len(Syn_Data.dataValues)*6)/6:
            excVref.append(Syn_Data[syninfo])

    SynIDX['delta'] = synang
    SynIDX['omega'] = synspeed
    SynIDX['p'] = synact
    SynIDX['q'] = synreact
    ExcIDX['vf'] = excVref
    ExcIDX['vm'] = excVmag

