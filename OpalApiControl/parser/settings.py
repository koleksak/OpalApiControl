from collections import defaultdict
from collections import Counter

paramKeys = ['Fault', 'Breaker', 'Pmu', 'Syn', 'Exc', 'Tg', 'Pss', 'Bus', 'Busfreq', 'SW', 'PV', 'PQ',
             'Shunt', 'Line', 'nBus', 'nLine', 'Wind', 'Dfig']


class Settings(object):
    """Object for storing System Parameters"""
    def __init__(self):
        self.SysParam = {}
        self.SysParamDevices = paramKeys
        self.Bus = []
        self.BusStore = {}  #For retrieving device parameter data while settings SysParams
        self.nBus = []
        self.BusNames = []
        self.Areas = []
        self.Regions = []
        self.PQ = []
        self.PV = []
        self.SW = []
        self.SWStore = {}   #For retrieving device parameter data while settings SysParams
        self.Shunt = []
        self.Syn = []
        self.SynStore = {}  #For retrieving device parameter data while settings SysParams
        self.Exc = []
        self.Tg = []
        self.govcount = 0
        self.LineOrd = defaultdict(list)
        self.linecount = 0
        self.Line = []
        self.nLine = []
        self.freq = 0
        self.Pss = []
        self.pss1count = 0  #TODO: Make Dictionary for holding count of PSS devices and name as well as Tg
        self.pss2count = 0
        self.Dfig = []
        self.Wind = []
        self.WindStore = {} #For retrieving device parameter data while settings SysParams
        self.Busfreq = []
        self.Pmu = []
        self.Breaker = []
        self.Fault = []
        self.DevicesAtBus =  defaultdict(list) #Stores the Dyr Devices at each bus to be used to generate I/0 ePHAS pins

    def set_sys_params(self):
        """Creates System Parameter Dict for attributes in the Class SysParamDevice List"""
        for device in self.SysParamDevices:
            if hasattr(self, str(device)):
                dev_values = self.__getattribute__(device)
                self.SysParam[device] = {}
                self.SysParam[device] = dev_values

