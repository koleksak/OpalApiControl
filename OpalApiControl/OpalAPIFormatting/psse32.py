"""PSS/E 32 file parser for ePhasorsim Models"""
NEVER = 60
CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
ALWAYS = 0
EMPTY = 0
pi = 3.14159265358973
jpi2 = 1.5707963267948966j
rad2deg = 57.295779513082323
deg2rad = 0.017453292519943
paramKeys = ['Fault','Breaker','Pmu','Syn','Exciter','TurGov','Pss','Bus','Busf','Sw','PV','PQ', \
             'Shunt', 'Line']
import logging
import os
import re
from collections import defaultdict
import stream
import idxvgs

SysParam = {}
Bus = []
BusParams = {}
BusNames = []
Areas = []
Zones = []
Load = {}
PQ = []
PQparams = {}
PV = []
PVparams = {}
SW = []
SWparams = {}
ShuntParams = {}
Shunt = []
Syn = []
SynParams = {}
LineParams = {}
LineOrd = defaultdict(list)
Line = []
Exc = []
Excparams = {}
freq = 0
Tg = []
Tgparams = {}
govcount = 0
Pss = []
Pssparams = {}
pss1count = 0
pss2count = 0
Dfig = []
Dfigparams = {}
Wind = []
Windparams = {}
Busfreq = []
Pmu = []

def testlines(fid):
    """Check the raw file for frequency base"""
    first = fid.readline()
    first = first.strip().split('/')
    first = first[0].split(',')
    if float(first[5]) == 50.0 or float(first[5]) == 60.0:
        return True
    else:
        return False


def read(file):
    """read PSS/E RAW file v32 format"""

    blocks = ['bus', 'load', 'fshunt', 'gen', 'branch', 'transf', 'area',
              'twotermdc', 'vscdc', 'impedcorr', 'mtdc', 'msline', 'zone',
              'interarea', 'owner', 'facts', 'swshunt', 'gne', 'Q']
    nol = [1, 1, 1, 1, 1, 4, 1,
           0, 0, 0, 0, 0, 1,
           0, 1, 0, 0, 0, 0]
    rawd = re.compile('rawd\d\d')

    retval = True
    version = 0
    b = 0  # current block index
    raw = {}
    for item in blocks:
        raw[item] = []

    data = []
    mdata = []  # multi-line data
    mline = 0  # line counter for multi-line models

    # parse file into raw with to_number conversions
    fid = open(file, 'r')
    for num, line in enumerate(fid.readlines()):
        line = line.strip()
        if num == 0:  # get basemva and frequency
            data = line.split('/')[0]
            data = data.split(',')

            mva = float(data[1])
            freq = float(data[5])
            version = int(data[2])

            if not version:
                version = int(rawd.search(line).group(0).strip('rawd'))
            if version < 32 or version > 33:
                logging.warning('RAW file version is not 32 or 33. Error may occur.')
            continue
        elif num == 1:  # store the case info line
            logging.info(line)
            continue
        elif num == 2:
            continue
        elif num >= 3:
            if line[0:2] == '0 ' or line[0:3] == ' 0 ':  # end of block
                b += 1
                continue
            elif line[0] is 'Q':  # end of file
                break
            data = line.split(',')

        data = [to_number(item) for item in data]
        mdata.append(data)
        mline += 1
        if mline == nol[b]:
            if nol[b] == 1:
                mdata = mdata[0]
            raw[blocks[b]].append(mdata)
            mdata = []
            mline = 0
    fid.close()

    # add device elements params and add to PSAT formatted dictionary


    for data in raw['bus']:
        """version 32:
          0,   1,      2,     3,    4,   5,  6,   7,  8
          ID, NAME, BasekV, Type, Area Zone Owner Va, Vm
        """
        idx = data[0]
        ty = data[3]
        angle = data[8]
        param = {'idx': idx,
                 'name': data[1],
                 'Vn': data[2],
                 'type': data[3],
                 'area': data[4],
                 'voltage': data[7],
                 'region': data[5],
                 'owner': data[6],
                 'angle': angle,
                 }

        psatlist = [data[0], data[2], data[8], angle, data[4], data[5]]
        Bus.append(psatlist)
        BusParams[data[0]] = param
        BusNames.append(data[1])
    # Add Bus Dictionary to Sys Param Dict
    SysParam['Bus'] = Bus
    SysParam['BusNames'] = BusNames

    maxV = 1.1
    minV = 0.9
    maxQ = 1
    minQ = 0
    convimp = 0
    status = 1
    loss = 1
    for data in raw['load']:
        """version 32:
          0,  1,      2,    3,    4,    5,    6,      7,   8,  9, 10,   11
        Bus, Id, Status, Area, Zone, PL(MW), QL (MW), IP, IQ, YP, YQ, OWNER
        """

        busidx = data[0]
        vn = BusParams[busidx]['Vn']
        voltage = BusParams[busidx]['voltage']
        param = {'bus': busidx,
                 'Vn': vn,
                 'Sn': mva,
                 'p': (data[5] + data[7] * voltage + data[9] * voltage ** 2) / mva,
                 'q': (data[6] + data[8] * voltage - data[10] * voltage ** 2) / mva,
                 'owner': data[11],
                 'type' : BusParams[busidx]['type'],
                 'voltage' : voltage
                 }

        if param['type'] == 1:

            psatlist = [busidx, mva,vn, param['p'], param['q'], maxV, minV, convimp, status]
            PQ.append(psatlist)
            PQparams[busidx] = param
            """CONFIRM THAT OTHER BUSES HAVE 0 P and 0 Q which are not added"""

        if param['type'] == 2:
            psatlist = [busidx, mva, vn, param['p'], voltage, maxQ, minQ, maxV, minV, loss, status]
            #PV.append(psatlist)
            PVparams[busidx] = param

        if param['type'] == 3:
            SWparams = param


        #For outside use
        Load[busidx] = param

    #Add PQ SysParam Dict. ADD PV, SW with Generator Data
    SysParam['PQ'] = PQ
    #SysParam['PV'] = PV
    #SysParam['SW'] = SW


    for data in raw['fshunt']:
        """
        0,    1,      2,      3,      4
        Bus, name, Status, g (MW), b (Mvar)
        """
        busidx = data[0]
        vn = BusParams[busidx]['Vn']
        param = {'bus': busidx,
                 'Vn': vn,
                 'status': data[2],
                 'Sn': mva,
                 'g': data[3] / mva,
                 'b': data[4] / mva,
                 }

        psatlist = [busidx, mva, vn, freq, param['g'], param['b'], param['status']]
        Shunt.append(psatlist)
        ShuntParams[busidx] = param

    #ADD SHUNT TO SYS PARAM DICT
    SysParam['Shunt'] = Shunt


    gen_idx = 0
    type = 6
    for data in raw['gen']:
        """
         0, 1, 2, 3, 4, 5, 6, 7,    8,   9,10,11, 12, 13, 14,   15, 16,17,18,19
         I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB,O1,F1
        """
        busidx = data[0]
        vn = BusParams[busidx]['Vn']
        gen_mva = data[8]
        gen_idx += 1
        status = data[14]
        leak = 0
        param = {'Sn': gen_mva,
                 'Vn': vn,
                 'u': status,
                 'idx': gen_idx,
                 'bus': busidx,
                 'pg': status*data[2]/mva,
                 'qg': status*data[3]/mva,
                 'qmax': data[4]/mva,
                 'qmin': data[5]/mva,
                 'v0': data[6],
                 'ra': data[9],  # ra  armature resistance
                 'xs': data[10],  # xs synchronous reactance
                 'pmax': data[16]/mva,
                 'pmin': data[17]/mva,
                 }

        if SWparams['bus'] == busidx:
            refangle = 0
            refBus = 1
            PGuess = 1
            swlist = [busidx, gen_mva, vn, SWparams['voltage'], refangle, param['qmax'], param['qmin'],
                      maxV, minV, PGuess, loss, refBus, status]
            SW = swlist
            SynParams[busidx] = param
            continue

        if busidx not in BusParams.keys():
            """ Need data from .dyr file.  Create initial list, then append data from .dyr"""
        else:
            #psatlist = [busidx, gen_mva, vn, freq, type, leak, param['ra'],param['xs']]
            #Syn.append(psatlist)
            SynParams[busidx] = param
            pvlist = [busidx, gen_mva, vn, param['pg'], BusParams[busidx]['voltage'],
                      param['qmax'], param['qmin'], maxV, minV, loss, status]
            PV.append(pvlist)

    #Don't Add to Sys params until .dyr data for generators appended (if any)
    #SysParam['Syn'] = Syn
    SysParam['PV'] = PV
    SysParam['SW'] = SW


    linelen = 0
    linecount = 0

    for data in raw['branch']:
        """
        I,J,CKT,R,X,B,RATEA,RATEB,RATEC,GI,BI,GJ,BJ,ST,LEN,O1,F1,...,O4,F4
        """
        param = {'bus1': data[0],
                 'bus2': data[1],
                 'r': data[3],
                 'x': data[4],
                 'b': data[5],
                 'rate_a': data[6],
                 'Vn': BusParams[data[0]]['Vn'],
                 'Vn2': BusParams[data[1]]['Vn'],
                 'length' : data[14],
                 'Ilim' : EMPTY,
                 'Plim' : EMPTY,
                 'Slim' : EMPTY,
                 'status' : data[13]
                 }

        psatlist = [param['bus1'], param['bus2'], param['rate_a'], param['Vn'], freq, EMPTY,
                    param['length'], param['r'], param['x'], param['b'], param['Ilim'], param['Plim'], EMPTY, EMPTY,
                    param['Slim'], param['status']]

        LineOrd[param['bus1']].append(psatlist)
        LineParams[linecount] = param
        linecount += 1

    #ADD Line Data to Sys Params Dict After Adding Transformer Data To Line


    for data in raw['transf']:
        """
        I,J,K,CKT,CW,CZ,CM,MAG1,MAG2,NMETR,'NAME',STAT,O1,F1,...,O4,F4
        R1-2,X1-2,SBASE1-2
        WINDV1,NOMV1,ANG1,RATA1,RATB1,RATC1,COD1,CONT1,RMA1,RMI1,VMA1,VMI1,NTP1,TAB1,CR1,CX1
        WINDV2,NOMV2
        """
        if len(data[1]) < 5:
            ty = 2
        else:
            ty = 3
        if ty == 3:
            raise NotImplementedError('Three-winding transformer not implemented')

        tap = data[2][0]
        phi = data[2][2]

        if tap == 1 and phi == 0:
            trasf = False
        else:
            trasf = True
        param = {'trasf': trasf,
                 'bus1': data[0][0],
                 'bus2': data[0][1],
                 'u': data[0][11],
                 'b': data[0][8],
                 'r': data[1][0],
                 'x': data[1][1],
                 'tap': tap,
                 'phi': phi,
                 'rate_a': data[2][3],
                 'Vn': BusParams[busidx]['Vn'],
                 'Vn2': BusParams[busidx]['Vn'],
                 #'length': data[?][?],  FIND CORRECT INDEX
                 'Ilim': EMPTY,
                 'Plim': EMPTY,
                 'Slim': EMPTY,
                 }
        psatlist = [param['bus1'], param['bus2'], param['rate_a'], param['Vn'], freq, EMPTY,
                EMPTY, param['r'], param['x'], param['b'], param['Ilim'], param['Plim'], EMPTY, EMPTY,
                param['Slim'], param['u']]

        LineOrd[param['bus1']].append(psatlist)
        LineParams[linecount] = param
        linecount += 1
    #ADD Line Data(All Branch Types) to Sys Param Dict after .dyr Transformer Data Added
    #Re-Order Line Data for correct sequence
    for key in LineOrd:
        for item in LineOrd[key]:
            Line.append(item)
    SysParam['Line'] = Line

    for data in raw['area']:
        Areas.append(data[4])
    SysParam['Areas'] = Areas

    for data in raw['zone']:
        Zones.append(data[1])

    SysParam['Regions'] = Zones

    return retval


#ADD Two Terminal DC Line
#ADD VSC DC Line
#ADD Impedance Correction
#ADD Multi-Terminal DC Line
#ADD Multi-Section Line
#ADD Inter-Area Transfer
#ADD Owner
#ADD FACTS
#ADD Switched Shunt
#ADD GNE

def readadd(file):
    """read DYR file"""
    dyr = {}
    data = []
    end = 0
    retval = True

    fid = open(file, 'r')
    for line in fid.readlines():
        if line.find('/') >= 0:
            line = line.split('/')[0]
            end = 1
        if line.find(',') >= 0:  # mixed comma and space splitter not allowed
            line = [to_number(item.strip()) for item in line.split(sep)]
        else:
            line = [to_number(item.strip()) for item in line.split()]
        if not line:
            end = 0
            continue
        data.extend(line)
        if end == 1:
            field = data[1]
            if field not in dyr.keys():
                dyr[field] = []
            dyr[field].append(data)
            end = 0
            data = []
    fid.close()

    # add device elements to system
    for model in dyr.keys():
        for data in dyr[model]:
            add_dyn(model, data)

    return retval



def add_dyn(model, data):
    """helper function to add a device element to system"""

    if model == 'GENCLS':
        busidx = data[0]
        data = data[3:]
        if busidx in PVparams.keys():
            dev = 'PV'
            gen_idx = busidx
        elif busidx in SWparams['bus']:
            dev = 'SW'
            gen_idx = busidx
        else:
            raise KeyError
        # todo: check xl
        param = {'bus': busidx,
                 'gen': gen_idx,
                 'Sn': SynParams[busidx]['Sn'],
                 'Vn': SynParams[busidx]['Vn'],
                 'type': 2,
                 'xd1': SynParams[busidx]['xs'],
                 'ra': SynParams['ra'],
                 'M': 2 * data[0],
                 'D': data[1],
                 }

        psatlist = [busidx, param['Sn'], param['Vn'], freq, param['type'], param['xl'], param['ra'],
                    param['xd1'], EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                    EMPTY,EMPTY, EMPTY, EMPTY, param['M'], param['D'],
                    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, param['status']]
        Syn.append(psatlist)

    elif model == 'GENROU':
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]
        else:
            raise KeyError
        param = {'bus': busidx,
                 'gen': gen_idx,
                 'Sn': SynParams[busidx]['Sn'],
                 'Vn': SynParams[busidx]['Vn'],
                 'ra': SynParams[busidx]['ra'],
                 'type': 6,
                 'Td10': data[0],
                 'Td20': data[1],
                 'Tq10': data[3],
                 'Tq20': data[4],
                 'M': 2 * data[4],
                 'D': data[5],
                 'xd': data[6],
                 'xq': data[7],
                 'xd1': data[8],
                 'xq1': data[9],
                 'xd2': data[10],
                 'xq2': data[10],  # xd2 = xq2
                 'xl': data[11],
                 'status' : 1
                 }

        psatlist = [busidx, param['Sn'], param['Vn'], freq, param['type'], param['xl'], param['ra'],
                    param['xd'], param['xd1'], param['xd2'], param['Td10'], param['Td20'], param['xq'],
                    param['xq1'], param['xq2'], param['Tq10'], param['Tq20'], param['M'], param['D'],
                    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, param['status']]
        Syn.append(psatlist)

    #CONFIRM EXCITER DATA, NEED SOME CALCULATIONS
    elif model == 'EXST1':
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype' : 1,  #Type 1 (PSAT TYPE II Params List)
                 'MTC': data[0],  # Measurement Time Constant T_r
                 'Vimax': data[1], #Voltage Integrator Output Max
                 'Vimin': data[2],
                 'Tc': data[3],  #AVR Lead Time Constant Tc
                 'Tb': data[4],  #AVR Lag
                 'excGain': data[5],  # K_a(Exciter Gain)
                 'regGain': EMPTY,
                 'Ta': data[6],  # Voltage regulator time constant
                 'maxregV': data[7],
                 'minregV': data[8],
                 'Kc': data[9], #Rectifier Loading factor
                 'Kf': data[10],#Field Voltage Feedback Gain(Stabilizer Gain)
                 'Tf': data[11], #Field Voltage Time Constant(Stabilizer Time Constant
                 '1stX': data[3],  #1st Pole(REGULATOR?)
                 '1st0': data[4],  #1st Zero(REGULATOR?)
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  #Field Circuit Time Constant  T_e
                 '1stCC': EMPTY,  #1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['excGain'],
                    param['Ta'], param['Kf'], param['Tf'], EMPTY, param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status']]

        Exc.append(psatlist)
        Excparams[busidx] = param


    elif model == 'IEEEX1':
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype': 1,  #Type 1
                 'MTC': data[0],  # Measurement Time Constant   T_r
                 'excGain': data[1],  # KA
                 'regGain': EMPTY,
                 'Ta': data[2],  # Exciter Time Constant
                 'Tb': data[3],  # AVR Lag Time Constant
                 'Tc': data[4],  # AVR Lead Time Constant
                 'maxregV': data[5],
                 'minregV': data[6],
                 'Ke': data[7],  #Field Circuit Integral Deviation
                 'FCTC': data[8],  # Field Circuit Time Constant  T_e
                 'Kf': data[9],  #Rate Feedback Gain(PSAT Stabilizer Gain
                 'Tf1': data[10],  #Stabilizer Time Constant
                 'Switch': 0,
                 'E1': data[12],  #Exciter Flux at Knee Curve(Saturation Voltage Point 1)
                 'SE_E1': data[13],  #Saturation Factor
                 'E2': data[14],
                 'SE_E2': data[15],
                 '1stX': EMPTY,  #1st Pole(REGULATOR?)
                 '1st0': EMPTY,  #1st Zero(REGULATOR?)
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 '1stCC': EMPTY,  #1st Ceiling Coefficient(PSAT Ae..COMPUTE)
                 '2ndCC': EMPTY,  #2nd Ceiling Coefficient(PSAT Be..COMPUTE)
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['Tc'], param['Tb'], param['2ndX'], param['2nd0'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status']]

        Exc.append(psatlist)
        Excparams[busidx] = param


    elif model == 'ESST3A':
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype' : 3,  #Type (Closest Brushless Type AC1A)
                 'MTC': data[0],  # Measurement Time Constant T_r
                 'Vimax': data[1], #Voltage Integrator Output Max
                 'Vimin': data[2],
                 'Km': data[3],
                 'Tc': data[4], #Lead Time Constant
                 'Tb': data[5], #Lag Time Constant
                 'regGain': data[6],
                 'Ta': data[7],  # Voltage regulator time constant
                 'maxregV': data[8],
                 'minregV': data[9],
                 'Kg': data[10],
                 'Kp': data[11],    #Voltage Reg. Proport. Gain
                 'Ki': data[12],    #Voltage Reg. Int. Gain
                 'Vbmax': data[13], #Voltage Base
                 'Kc': data[14], #Rectifier Loading factor
                 'xl': data[15], #leakage
                 'Vgmax': data[16], #???
                 'theta_p': data[17], #???
                 'Tm': data[18],    #???
                 'Vmmax': data[19], #???
                 'Vmmin': data[20], #???
                 '1stX': EMPTY,  #1st Pole
                 '1st0': EMPTY,  #1st Zero
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  #Field Circuit Time Constant
                 '1stCC': EMPTY,  #1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['Tc'], param['Tb'], param['2ndX'], param['Ta'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status']]

        Exc.append(psatlist)
        Excparams[busidx] = param

    elif model == 'ESST4B':
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype' : 4,  #Type ST4B
                 'maxregV': data[3],
                 'minregV': data[4],
                 'Ta': data[5],  # Voltage regulator time constant(Bridge)
                 'Kpm': data[6], #???
                 'Kim': data[7], #???
                 'Vmmax': data[8], #???
                 'Vmmin': data[9],
                 'Kg': data[10], #???
                 'Kp': data[11],    #Voltage Reg. Proport. Gain
                 'Ki': data[12],    #Voltage Reg. Integ. Gain
                 'Vbmax': data[13], #Voltage Base
                 'Kc': data[14],  # Rectifier Loading factor
                 'xl': data[15],  # leakage
                 'theta_p': data[16], # ???
                 'regGain': EMPTY,  #ADD UP K'S Gain??
                 '1stX': EMPTY,  #1st Pole
                 '1st0': EMPTY,  #1st Zero
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  #Field Circuit Time Constant
                 'MTC': EMPTY,  #Measurement Time Constant
                 '1stCC': EMPTY,  #1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['1stX'], param['1st0'], param['2ndX'], param['2nd0'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status']]

        Exc.append(psatlist)
        Excparams[busidx] = param

    elif model == 'IEEEG1':
        global govcount
        govcount += 1
        busidx = data[0]
        data = data[5:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'type': 1,
                 'ref_speed': EMPTY,
                 'Droop': EMPTY,
                 'maxTO': EMPTY,
                 'minTO': EMPTY,
                 'govTC': EMPTY,
                 'servoTC': EMPTY,
                 'tgTC': EMPTY, #Transient Gain Time Constant
                 'pfTC': EMPTY, #Power Fraction Time Constant
                 'rTC': EMPTY, #Reheat Time Constant
                 'status': 1
                 }
        psatlist = [busidx, param['type'], param['ref_speed'], param['Droop'], param['maxTO'], param['minTO'],
                    param['govTC'], param['servoTC'], param['tgTC'], param['pfTC'], param['rTC'], param['status']]

        Tg.append(psatlist)
        Tgparams[busidx] = param

    elif model == 'IEE2ST':
        global pss2count
        pss2count += 1
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'type': 1,
                 'AVR': pss2count,
                 'PSSmodel': 1,
                 'PSSin': 1,
                 'Vmaxsout': EMPTY,
                 'Vminsout': EMPTY,
                 'Kw': EMPTY, #Stabilizer Gain
                 'Tw': EMPTY, #Washout Time
                 'T1': data[2], #1st Lead
                 'T2': data[3], #1st Lag
                 'T3': data[4], #2nd
                 'T4': data[5],
                 'T5': data[6], #3rd
                 'T6': data[7],
                 'T7': data[8], #Filter Lead Time Constant
                 'T8': data[9], #Filter Lag
                 'T9': data[10], #Freq Branch Time Constant
                 'T10': data[11], #Power Branch Time Constant
                 'Lsmax': data[12],
                 'Lsmin': data[13],
                 'Vcu': data[14],
                 'Vcl': data[15],
                 'Ka': EMPTY, #Gain for additional signal
                 'Ta': EMPTY, #Time constant for additional signal
                 'Kp': EMPTY, #Gain for active power
                 'Kv': EMPTY, #Gain for bus voltage magnitude
                 'Vamax': EMPTY, #additonal signal(anti-windup)
                 'Vamin': EMPTY, #additional signal(windup)
                 'Vsmax': EMPTY, #max output(no additonal)
                 'Vsmin': EMPTY, #min output(no additional)
                 'FVthresh': EMPTY,
                 'RSthresh': EMPTY,
                 'switch': 1,
                 'status': 1,
                 }

        psatlist = [param['AVR'], param['PSSmodel'], param['PSSin'], param['Vsmax'], param['Vsmin'], param['Kw'],
                    param['Tw'], param['T1'], param['T2'], param['T3'], param['T4'], param['Ka'], param['Ta'],
                    param['Kp'], param['Kv'], param['Vamax'], param['Vamin'], param['Vsmax'], param['Vsmin'],
                    param['FVthresh'], param['RSthresh'], param['switch'], param['status']]

        Pss.append(psatlist)
        Pssparams[busidx] = param

    elif model == 'IEEEST':
        global pss1count
        pss1count += 1
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'type': 0,
                 'AVR': pss1count,
                 'PSSmodel': 1,
                 'PSSin': 1,
                 'Vmaxsout': EMPTY,
                 'Vminsout': EMPTY,
                 'Kw': EMPTY, #Stabilizer Gain
                 'Tw': EMPTY, #Washout Time
                 'A1': data[0],
                 'A2': data[1],
                 'A3': data[2],
                 'A4': data[3],
                 'A5': data[4],
                 'A6': data[5],
                 'T1': data[6],
                 'T2': data[7],
                 'T3': data[8],
                 'T4': data[9],
                 'T5': data[10],
                 'T6': data[11],
                 'Ks': data[12],
                 'Lsmax': data[13],
                 'Lsmin': data[14],
                 'Vcu': data[15],
                 'Vcl': data[16],
                 'Ka': EMPTY, #Gain for additional signal
                 'Ta': EMPTY, #Time constant for additional signal
                 'Kp': EMPTY, #Gain for active power
                 'Kv': EMPTY, #Gain for bus voltage magnitude
                 'Vamax': EMPTY, #additonal signal(anti-windup)
                 'Vamin': EMPTY, #additional signal(windup)
                 'Vsmax': EMPTY, #max output(no additonal)
                 'Vsmin': EMPTY, #min output(no additional)
                 'FVthresh': EMPTY,
                 'RSthresh': EMPTY,
                 'switch': 1,
                 'status': 1,
                 }

        psatlist = [param['AVR'], param['PSSmodel'], param['PSSin'], param['Vsmax'], param['Vsmin'], param['Kw'],
                    param['Tw'], param['T1'], param['T2'], param['T3'], param['T4'], param['Ka'], param['Ta'],
                    param['Kp'], param['Kv'], param['Vamax'], param['Vamin'], param['Vsmax'], param['Vsmin'],
                    param['FVthresh'], param['RSthresh'], param['switch'], param['status']]

        Pss.append(psatlist)
        Pssparams[busidx] = param

    elif model == 'DFIG':
        busidx = data[0]
        data = data[2:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'bus': busidx,
                 'speednum': data[0],
                 'Sn': EMPTY,
                 'Vn': 20,
                 'freq': 60,
                 'Rs': EMPTY,
                 'Xs': data[1],
                 'Rr': EMPTY,
                 'Xr': data[4],
                 'Xu': EMPTY,
                 'Hm': data[2],
                 'Kp': EMPTY,
                 'Tp': EMPTY,
                 'Kv': EMPTY,
                 'Teps': EMPTY,
                 'R': EMPTY,
                 'npoles': EMPTY,
                 'nb': EMPTY,
                 'nGB': EMPTY,
                 'pmax': EMPTY,
                 'pmin': EMPTY,
                 'qmax': EMPTY,
                 'qmin': EMPTY,
                 'status': data[0],
                 }

        psatlist = [busidx, param['speednum'], param['Sn'], param['Vn'], param['freq'], param['Rs'],
                    param['Xs'], param['Rr'], param['Xr'], param['Xu'], param['Hm'], param['Kp'],
                    param['Tp'], param['Kv'], param['Teps'], param['R'], param['npoles'], param['nb'],
                    param['nGB'], param['pmax'], param['pmin'], param['qmin'], param['qmin'], param['status']]

        Dfig.append(psatlist)
        Dfigparams[busidx] = param

    elif model == 'WTE':
        #Type 1 and 2
        busidx = data[0]
        data = data[2:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'model': data[0],
                 'nomspeed': 13,
                 'airdens': 1.225,
                 'tau': 4,
                 'delT': 0.1,
                 'c': 20,
                 'k': 2,
                 'Tsr': 5,
                 'Ter': 15,
                 'Vwr': 0,
                 'Tsg': 5,
                 'Teg': 15,
                 'Vwg': 0,
                 'Z0': 0.01,
                 'fstep': 0.2,
                 'nharm': 50
                 }
        psatlist = [param['model'], param['nomspeed'], param['airdens'], param['tau'],
                    param['delT'], param['c'],param['k'], param['Tsr'], param['Ter'], param['Vwr'],
                    Windparams[busidx]['H'], param['Tsg'], param['Teg'], param['Vwg'], param['Z0'],
                    param['fstep'], param['nharm']]

        Windparams[busidx].update(param)
        Wind.append(psatlist)


    elif model == 'WTT':
        #Type 1 and 2
        busidx = data[0]
        data = data[3:]
        if busidx in BusParams.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx == SW[0]:
            dev = 'SW'
            gen_idx = SW[0]

        else:
            raise KeyError

        param = {'H': data[0],
                 'Damp': EMPTY,
                 'Htf': EMPTY,
                 'Freq1': EMPTY,
                 'Dshaft': EMPTY
                 }

        Windparams[busidx] = param

    else:
        logging.warning('Skipping unsupported mode <{}> on bus {}'.format(model, data[0]))


def to_number(s):
    """Convert a string to a number. If not successful, return the string without blanks"""
    ret = s
    try:
        ret = float(s)
    except ValueError:
        ret = ret.strip('\'').strip()
        return ret

    try:
        ret = int(s)
    except ValueError:
        pass
    return ret

if __name__ == '__main__':
    project = 'ephasorFormat1'
    rawfile = 'Curent02_final'
    dyrfile = 'Curent02_final_Wind'
    projectPath = 'C:/Users/Kellen/OPAL-RT/RT-LABv11_Workspace/'
    projectName = os.path.join(projectPath, str(project) + '/')
    filePath = os.path.join(projectName, 'simulink/')
    powfile = os.path.join(filePath, rawfile + '.raw')
    dynfile = os.path.join(filePath,dyrfile + '.dyr')

    read(powfile)
    readadd(dynfile)
    SysParam['Syn'] = Syn
    SysParam['Exc'] = Exc
    SysParam['Tg'] = Tg
    SysParam['Pss'] = Pss
    SysParam['Dfig'] = Dfig
    SysParam['Wind'] = Wind
    #Add PMU(must calculate)
    for bus in range(0,len(SysParam['Bus'])):
        data = [bus+2, 0.001, 0.001, 1]
        Busfreq.append(data)
    SysParam['Busfreq'] = Busfreq

    for bus in range(0,len(SysParam['Bus'])):
        data = [bus+2, BusParams[bus+2]['Vn'], 60, 0.05, 0.05, 1, 30, 2, 0]
        Pmu.append(data)
    SysParam['Pmu'] = Pmu

    print('******Sys Param Dict : Buses*******')
    for item in SysParam['Bus']:
        print(item)
    print('******Sys Param Dict : Generators*******')
    for item in SysParam['Syn']:
        print(item)

    #ADD WIND

    print('******Sys Param Dict : PQ*******')
    for item in SysParam['PQ']:
        print(item)
    print('******Sys Param Dict : PV*******')
    for item in SysParam['PV']:
        print(item)
    print('******Sys Param Dict : Lines*******')
    for item in SysParam['Line']:
        print(item)
    print('******Sys Param Dict : Shunt*******')
    for item in SysParam['Shunt']:
        print(item)
    print('******Sys Param Dict : SW*******')
    print(SysParam['SW'])
    print('******Sys Param Dict : Exciters*******')
    for item in SysParam['Exc']:
        print(item)
    print('******Sys Param Dict : Governors*******')
    for item in SysParam['Tg']:
        print(item)
    print('******Sys Param Dict : System Stabilizers*******')
    for item in SysParam['Pss']:
        print(item)
    print('******Sys Param Dict : Double Fed Induction Gen*******')
    for item in SysParam['Dfig']:
        print(item)
    print('******Sys Param Dict : Wind*******')
    for item in SysParam['Wind']:
        print(item)
    print('******Sys Param Dict : Busfreq*******')
    for item in SysParam['Busfreq']:
        print(item)
    print('******Sys Param Dict : Pmu*******')
    for item in SysParam['Pmu']:
        print(item)
    print('******Sys Param Dict : Bus Names*******')
    for item in SysParam['BusNames']:
        print(item)
    print('******Sys Param Dict : Areas*******')
    for item in SysParam['Areas']:
        print(item)
    print('******Sys Param Dict : Regions*******')
    for item in SysParam['Regions']:
        print(item)


    print('Set Idxvgs')
    idxvgs.set_idxvgs(SysParam)


    print('Set Varheader')
    idxvgs.set_varheader()
    idxvgs.check_set_varheader()
    idxvgs.var_idx_vgs_list()

    if(stream.set_dime_connect('SE','tcp://127.0.0.1:5000/dime')):
        stream.send_varhead_idxvgs()


