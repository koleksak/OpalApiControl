"""PSS/E 32 file parser for ePhasorsim Models"""
import logging
import os
import re

from settings import Settings

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

global Settings
Settings = Settings()

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
          0,   1,      2,     3,    4,   5,  6,   7,  8,   9,           10
          ID, NAME, BasekV, Type, Area Zone Owner Va, Vm,  latitude     longitude
        """
        idx = data[0]
        ty = data[3]
        angle = data[8]
        try:
            lat = data[9]
        except:
            # logging.warning('<No Coordinates in .raw file>')
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
            psatlist = [data[0], data[2], data[7], angle, data[4], data[5]]
        else:
            param = {'idx': idx,
                     'name': data[1],
                     'Vn': data[2],
                     'type': data[3],
                     'area': data[4],
                     'voltage': data[7],
                     'region': data[5],
                     'owner': data[6],
                     'angle': angle,
                     'latitude': data[9],
                     'longitude': data[10]
                     }
            psatlist = [data[0], data[2], data[7], angle, data[4], data[5], data[9], data[10]]
        Settings.Bus.append(psatlist)
        Settings.BusNames.append(data[1])
        # Add BusSTORE Dictionary For Later Reference
        Settings.BusStore[idx] = param

    xcoord = [34.560040, 34.938385, 34.360040, 40.5152473, 40.3142473, 36.527401, 36.857401, 36.687401, 36.856401,
              40.487041, 36.903901, 36.702901, 35.832561, 33.386047, 33.185047, 37.105571, 37.104154, 33.706718,
              37.103549, 36.703539, 37.103559, 36.703549, 36.033561, 35.631561, 36.032561, 35.732561, 36.525401,
              36.857401, 49.869314, 50.969314, 51.979314, 52.481674, 54.973192, 56.276212, 41.734596, 34.551015,
              34.652015, 34.537507, 34.587507, 34.157904, 33.714453, 33.762453, 39.548160, 39.496160, 34.313143,
              34.545782, 34.380686, 34.111686, 34.137762, 34.118650, 34.158650, 33.918650, 33.718650, 34.018650,
              34.018650, 34.018650, 34.018650, 34.018650, 34.312456, 34.315456, 34.243600, 34.566258, 34.565258,
              46.064672, 46.565672, 45.514571, 45.606833, 45.806833, 44.890000, 45.596416, 45.295416, 45.891161,
              47.954899, 46.511440, 45.913936, 45.713936, 46.669335, 47.954899, 47.624154, 43.784730, 44.482350,
              42.006860, 42.934919, 42.731919, 43.013135, 44.068350, 43.558350, 42.438350, 42.938350, 44.068350,
              43.558350, 43.048350, 42.638350, 44.068350, 43.558350, 43.048350, 42.638350, 43.620189, 39.120428,
              40.398031, 35.216200, 35.215200, 36.202099, 39.777745, 39.539598, 37.052929, 35.403217, 35.352217,
              36.807243, 39.567450, 40.807689, 40.806689, 41.008689, 39.555494, 37.954721, 38.406721, 38.906721,
              38.656721]
    ycoord = [-109.277313, -110.303798, -109.777313, -107.546455, -107.546455, -108.325669, -108.654569, -108.486669,
              -108.325669, -107.185575, -111.390408, -111.390408, -111.448566, -112.860397, -112.659397, -108.243555,
              -108.441191, -112.322033, -111.590816, -111.190816, -111.190816, -111.590806, -111.648566, -111.248566,
              -111.249566, -111.647566, -108.655669, -108.323669, -122.150895, -122.150895, -122.150895, -121.61684,
              -121.924221, -122.21370, -108.790427, -117.568105, -117.538105, -118.607375, -118.658375, -118.280282,
              -118.146319, -118.096319, -112.52797, -112.72797, -118.690631, -118.389938, -118.478496, -118.478496,
              -118.299917, -118.095428, -118.095428, -118.095428, -118.095428, -118.195428, -118.395428, -117.995428,
              -117.795428, -117.995428, -118.481217, -118.891217, -118.391667, -117.166428, -117.368428, -106.60906,
              -106.80906, -122.681289, -121.114785, -122.113785, -123.29000, -121.312202, -121.114202, -106.612578,
              -118.997945, -112.88531, -120.692286, -120.693974, -119.571501, -120.997945, -122.219492, -118.77463,
              -121.019484, -121.316546, -114.419206, -114.419206, -120.956476, -120.79484, -120.93484, -121.216546,
              -121.156546, -121.215484, -121.135484, -121.255484, -121.175484, -121.013484, -120.733484, -121.053484,
              -120.973484, -118.865882, -122.073631, -122.263453, -120.847567, -120.900567, -120.129849, -122.142965,
              -122.262993, -121.021929, -119.450452, -119.450452, -121.779037, -122.276225, -122.135718, -121.935718,
              -121.935718, -121.24000, -121.18379, -121.10879, -121.27379, -121.23979]

    #for idx, line in enumerate(Settings.Bus):
    #    line.extend([xcoord[idx], ycoord[idx]])

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
        vn = Settings.BusStore[busidx]['Vn']
        voltage = Settings.BusStore[busidx]['voltage']
        param = {'bus': busidx,
                 'Vn': vn,
                 'Sn': mva,
                 'p': (data[5] + data[7] * voltage + data[9] * voltage ** 2) / mva,
                 'q': (data[6] + data[8] * voltage - data[10] * voltage ** 2) / mva,
                 'owner': data[11],
                 'type': Settings.BusStore[busidx]['type'],
                 'voltage': voltage
                 }

        psatlist = [busidx, mva, vn, param['p'], param['q'], maxV, minV, convimp, status]
        Settings.PQ.append(psatlist)
        """CONFIRM THAT OTHER BUSES HAVE 0 P and 0 Q which are not added"""

    for data in raw['fshunt']:
        """
        0,    1,      2,      3,      4
        Bus, name, Status, g (MW), b (Mvar)
        """
        busidx = data[0]
        vn = Settings.BusStore[busidx]['Vn']
        param = {'bus': busidx,
                 'Vn': vn,
                 'status': data[2],
                 'Sn': mva,
                 'g': data[3] / mva,
                 'b': data[4] / mva,
                 }

        psatlist = [busidx, mva, vn, freq, param['g'], param['b'], param['status']]
        Settings.Shunt.append(psatlist)

    gen_idx = 0
    type = 6

    for data in raw['gen']:
        """
         0, 1, 2, 3, 4, 5, 6, 7,    8,   9,10,11, 12, 13, 14,   15, 16,17,18,19
         I,ID,PG,QG,QT,QB,VS,IREG,MBASE,ZR,ZX,RT,XT,GTAP,STAT,RMPCT,PT,PB,O1,F1
        """
        busidx = data[0]
        vn = Settings.BusStore[busidx]['Vn']
        gen_mva = data[8]
        gen_idx += 1
        status = data[14]
        leak = 0
        param = {'Sn': gen_mva,
                 'Vn': vn,
                 'u': status,
                 'idx': gen_idx,
                 'bus': busidx,
                 'pg': status * data[2] / mva,
                 'qg': status * data[3] / mva,
                 'qmax': data[4] / mva,
                 'qmin': data[5] / mva,
                 'v0': data[6],
                 'ra': data[9],  # ra  armature resistance
                 'xs': data[10],  # xs synchronous reactance
                 'pmax': data[16] / mva,
                 'pmin': data[17] / mva,
                 }

        if Settings.BusStore[busidx]['type'] == 3:  #Check Bus Type for Slack
            refangle = 0
            refBus = 1
            PGuess = 1
            swlist = [busidx, gen_mva, vn, param['v0'], refangle, param['qmax'], param['qmin'],
                      maxV, minV, PGuess, loss, refBus, status]
            SW = swlist
            Settings.SW.append(swlist)
            Settings.SWStore[busidx] = param
            Settings.SynStore[busidx] = param
            continue

        if busidx not in Settings.BusStore.keys():
            """ Need data from .dyr file.  Create initial list, then append data from .dyr"""
        else:
            # psatlist = [busidx, gen_mva, vn, freq, type, leak, param['ra'],param['xs']]
            # Syn.append(psatlist)
            Settings.SynStore[busidx] = param
            pvlist = [busidx, gen_mva, vn, param['pg'], Settings.BusStore[busidx]['voltage'],
                      param['qmax'], param['qmin'], maxV, minV, loss, status]
            Settings.PV.append(pvlist)


    for data in raw['branch']:
        """
        I,J,ID,R,X,B,RATEA,RATEB,RATEC,GI,BI,GJ,BJ,ST,LEN,O1,F1,...,O4,F4
        """
        param = {'bus1': data[0],
                 'bus2': data[1],
                 'id' : data[2],
                 'r': data[3],
                 'x': data[4],
                 'b': data[5],
                 'rate_a': data[6],
                 'rate_b': data[7],
                 'rate_c': data[8],
                 'Vn': Settings.BusStore[data[0]]['Vn'],
                 'Vn2': Settings.BusStore[data[1]]['Vn'],
                 'length': data[14],
                 'Ilim': EMPTY,
                 'Plim': EMPTY,
                 'Slim': EMPTY,
                 'status': data[13]
                 }

        psatlist = [param['bus1'], param['bus2'], param['rate_c'], param['Vn'], freq, EMPTY,
                    param['length'], param['r'], param['x'], param['b'], param['Ilim'], param['Plim'], EMPTY, EMPTY,
                    param['Slim'], param['status']]
        Settings.Lineij.append([data[0], data[1], data[2]])
        Settings.Lineji.append([data[1], data[0], data[2]])
        Settings.LineOrd[param['bus1']].append(psatlist)
        Settings.LineBusMatij[param['bus2']].append(Settings.linecount)
        Settings.LineBusMatji[param['bus1']].append(Settings.linecount)
        Settings.linecount += 1

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
            continue
            # raise NotImplementedError('Three-winding transformer not implemented')

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
                 'Vn': Settings.BusStore[busidx]['Vn'],
                 'Vn2': Settings.BusStore[busidx]['Vn'],
                 # 'length': data[?][?],  FIND CORRECT INDEX
                 'Ilim': EMPTY,
                 'Plim': EMPTY,
                 'Slim': EMPTY,
                 }
        psatlist = [param['bus1'], param['bus2'], param['rate_a'], param['Vn'], freq, EMPTY,
                    EMPTY, param['r'], param['x'], param['b'], param['Ilim'], param['Plim'], EMPTY, EMPTY,
                    param['Slim'], param['u']]

        Settings.LineOrd[param['bus1']].append(psatlist)
        Settings.linecount += 1
    # ADD Line Data(All Branch Types) to Sys Param Dict after .dyr Transformer Data Added
    # Re-Order Line Data for correct sequence
    for key in Settings.LineOrd:
        for item in Settings.LineOrd[key]:
            Settings.Line.append(item)

    for data in raw['area']:
        Settings.Areas.append(data[4])

    for data in raw['zone']:
        Settings.Regions.append(data[1])

    return retval

# ADD Two Terminal DC Line
# ADD VSC DC Line
# ADD Impedance Correction
# ADD Multi-Terminal DC Line
# ADD Multi-Section Line
# ADD Inter-Area Transfer
# ADD Owner
# ADD FACTS
# ADD Switched Shunt
# ADD GNE


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
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx
        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx
        else:
            raise KeyError
        # todo: check xl
        param = {'bus': busidx,
                 'gen': gen_idx,
                 'Sn': Settings.SynStore[busidx]['Sn'],
                 'Vn': Settings.SynStore[busidx]['Vn'],
                 'type': 2,
                 'xd1': Settings.SynStore[busidx]['xs'],
                 'ra': Settings.SynStore[busidx]['ra'],
                 'M': 2 * data[0],
                 'D': data[1],
                 'xl': 0,  # TODO: retrieve `xl` from raw file
                 'status': 1,  # TODO: retrieve `u` from raw file
                 }

        psatlist = [busidx, param['Sn'], param['Vn'], Settings.freq, param['type'], param['xl'], param['ra'],
                    param['xd1'], EMPTY, EMPTY, EMPTY, EMPTY, EMPTY,
                    EMPTY, EMPTY, EMPTY, EMPTY, param['M'], param['D'],
                    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, param['status']]
        Settings.Syn.append(psatlist)
        Settings.DevicesAtBus[busidx].append({'Bus': busidx , 'Id' : id})


    elif model == 'GENROU':
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SW.keys():
            dev = 'SW'
            gen_idx = busidx
        else:
            raise KeyError
        param = {'bus': busidx,
                 'gen': gen_idx,
                 'Sn': Settings.SynStore[busidx]['Sn'],
                 'Vn': Settings.SynStore[busidx]['Vn'],
                 'ra': Settings.SynStore[busidx]['ra'],
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
                 'status': 1
                 }

        psatlist = [busidx, param['Sn'], param['Vn'], Settings.freq, param['type'], param['xl'], param['ra'],
                    param['xd'], param['xd1'], param['xd2'], param['Td10'], param['Td20'], param['xq'],
                    param['xq1'], param['xq2'], param['Tq10'], param['Tq20'], param['M'], param['D'],
                    EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, param['status']]
        Settings.Syn.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    # CONFIRM EXCITER DATA, NEED SOME CALCULATIONS
    elif model == 'EXST1':
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype': 1,  # Type 1 (PSAT TYPE II Params List)
                 'MTC': data[0],  # Measurement Time Constant T_r
                 'Vimax': data[1],  # Voltage Integrator Output Max
                 'Vimin': data[2],
                 'Tc': data[3],  # AVR Lead Time Constant Tc
                 'Tb': data[4],  # AVR Lag
                 'excGain': data[5],  # K_a(Exciter Gain)
                 'regGain': EMPTY,
                 'Ta': data[6],  # Voltage regulator time constant
                 'maxregV': data[7],
                 'minregV': data[8],
                 'Kc': data[9],  # Rectifier Loading factor
                 'Kf': data[10],  # Field Voltage Feedback Gain(Stabilizer Gain)
                 'Tf': data[11],  # Field Voltage Time Constant(Stabilizer Time Constant
                 '1stX': data[3],  # 1st Pole(REGULATOR?)
                 '1st0': data[4],  # 1st Zero(REGULATOR?)
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  # Field Circuit Time Constant  T_e
                 '1stCC': EMPTY,  # 1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['excGain'],
                    param['Ta'], param['Kf'], param['Tf'], EMPTY, param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status'], 0]

        Settings.Exc.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'IEEEX1':
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype': 1,  # Type 1
                 'MTC': data[0],  # Measurement Time Constant   T_r
                 'excGain': data[1],  # KA
                 'regGain': EMPTY,
                 'Ta': data[2],  # Exciter Time Constant
                 'Tb': data[3],  # AVR Lag Time Constant
                 'Tc': data[4],  # AVR Lead Time Constant
                 'maxregV': data[5],
                 'minregV': data[6],
                 'Ke': data[7],  # Field Circuit Integral Deviation
                 'FCTC': data[8],  # Field Circuit Time Constant  T_e
                 'Kf': data[9],  # Rate Feedback Gain(PSAT Stabilizer Gain
                 'Tf1': data[10],  # Stabilizer Time Constant
                 'Switch': 0,
                 'E1': data[12],  # Exciter Flux at Knee Curve(Saturation Voltage Point 1)
                 'SE_E1': data[13],  # Saturation Factor
                 'E2': data[14],
                 'SE_E2': data[15],
                 '1stX': EMPTY,  # 1st Pole(REGULATOR?)
                 '1st0': EMPTY,  # 1st Zero(REGULATOR?)
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 '1stCC': EMPTY,  # 1st Ceiling Coefficient(PSAT Ae..COMPUTE)
                 '2ndCC': EMPTY,  # 2nd Ceiling Coefficient(PSAT Be..COMPUTE)
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['Tc'], param['Tb'], param['2ndX'], param['2nd0'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status'], 0]

        Settings.Exc.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'ESST3A':
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype': 3,  # Type (Closest Brushless Type AC1A)
                 'MTC': data[0],  # Measurement Time Constant T_r
                 'Vimax': data[1],  # Voltage Integrator Output Max
                 'Vimin': data[2],
                 'Km': data[3],
                 'Tc': data[4],  # Lead Time Constant
                 'Tb': data[5],  # Lag Time Constant
                 'regGain': data[6],
                 'Ta': data[7],  # Voltage regulator time constant
                 'maxregV': data[8],
                 'minregV': data[9],
                 'Kg': data[10],
                 'Kp': data[11],  # Voltage Reg. Proport. Gain
                 'Ki': data[12],  # Voltage Reg. Int. Gain
                 'Vbmax': data[13],  # Voltage Base
                 'Kc': data[14],  # Rectifier Loading factor
                 'xl': data[15],  # leakage
                 'Vgmax': data[16],  # ???
                 'theta_p': data[17],  # ???
                 'Tm': data[18],  # ???
                 'Vmmax': data[19],  # ???
                 'Vmmin': data[20],  # ???
                 '1stX': EMPTY,  # 1st Pole
                 '1st0': EMPTY,  # 1st Zero
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  # Field Circuit Time Constant
                 '1stCC': EMPTY,  # 1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['Tc'], param['Tb'], param['2ndX'], param['Ta'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status'], 0]

        Settings.Exc.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'ESST4B':
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'extype': 4,  # Type ST4B
                 'maxregV': data[3],
                 'minregV': data[4],
                 'Ta': data[5],  # Voltage regulator time constant(Bridge)
                 'Kpm': data[6],  # ???
                 'Kim': data[7],  # ???
                 'Vmmax': data[8],  # ???
                 'Vmmin': data[9],
                 'Kg': data[10],  # ???
                 'Kp': data[11],  # Voltage Reg. Proport. Gain
                 'Ki': data[12],  # Voltage Reg. Integ. Gain
                 'Vbmax': data[13],  # Voltage Base
                 'Kc': data[14],  # Rectifier Loading factor
                 'xl': data[15],  # leakage
                 'theta_p': data[16],  # ???
                 'regGain': EMPTY,  # ADD UP K'S Gain??
                 '1stX': EMPTY,  # 1st Pole
                 '1st0': EMPTY,  # 1st Zero
                 '2ndX': EMPTY,
                 '2nd0': EMPTY,
                 'FCTC': EMPTY,  # Field Circuit Time Constant
                 'MTC': EMPTY,  # Measurement Time Constant
                 '1stCC': EMPTY,  # 1st Ceiling Coefficient
                 '2ndCC': EMPTY,
                 'status': 1
                 }
        psatlist = [gen_idx, param['extype'], param['maxregV'], param['minregV'], param['regGain'],
                    param['1stX'], param['1st0'], param['2ndX'], param['2nd0'], param['FCTC'],
                    param['MTC'], param['1stCC'], param['2ndCC'], param['status'], 0]

        Settings.Exc.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'IEEEG1':
        Settings.govcount += 1
        busidx = data[0]
        id = data[2]
        data = data[5:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

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
                 'tgTC': EMPTY,  # Transient Gain Time Constant
                 'pfTC': EMPTY,  # Power Fraction Time Constant
                 'rTC': EMPTY,  # Reheat Time Constant
                 'status': 1
                 }
        psatlist = [busidx, param['type'], param['ref_speed'], param['Droop'], param['maxTO'], param['minTO'],
                    param['govTC'], param['servoTC'], param['tgTC'], param['pfTC'], param['rTC'], param['status']]

        Settings.Tg.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'IEE2ST':

        Settings.pss2count += 1
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'type': 1,
                 'AVR': Settings.pss2count,
                 'PSSmodel': 1,
                 'PSSin': 1,
                 'Vmaxsout': EMPTY,
                 'Vminsout': EMPTY,
                 'Kw': EMPTY,  # Stabilizer Gain
                 'Tw': EMPTY,  # Washout Time
                 'T1': data[2],  # 1st Lead
                 'T2': data[3],  # 1st Lag
                 'T3': data[4],  # 2nd
                 'T4': data[5],
                 'T5': data[6],  # 3rd
                 'T6': data[7],
                 'T7': data[8],  # Filter Lead Time Constant
                 'T8': data[9],  # Filter Lag
                 'T9': data[10],  # Freq Branch Time Constant
                 'T10': data[11],  # Power Branch Time Constant
                 'Lsmax': data[12],
                 'Lsmin': data[13],
                 'Vcu': data[14],
                 'Vcl': data[15],
                 'Ka': EMPTY,  # Gain for additional signal
                 'Ta': EMPTY,  # Time constant for additional signal
                 'Kp': EMPTY,  # Gain for active power
                 'Kv': EMPTY,  # Gain for bus voltage magnitude
                 'Vamax': EMPTY,  # additonal signal(anti-windup)
                 'Vamin': EMPTY,  # additional signal(windup)
                 'Vsmax': EMPTY,  # max output(no additonal)
                 'Vsmin': EMPTY,  # min output(no additional)
                 'FVthresh': EMPTY,
                 'RSthresh': EMPTY,
                 'switch': 1,
                 'status': 1,
                 }

        psatlist = [param['AVR'], param['PSSmodel'], param['PSSin'], param['Vsmax'], param['Vsmin'], param['Kw'],
                    param['Tw'], param['T1'], param['T2'], param['T3'], param['T4'], param['Ka'], param['Ta'],
                    param['Kp'], param['Kv'], param['Vamax'], param['Vamin'], param['Vsmax'], param['Vsmin'],
                    param['FVthresh'], param['RSthresh'], param['switch'], param['status']]

        Settings.Pss.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'IEEEST':
        Settings.pss1count += 1
        busidx = data[0]
        id = data[2]
        data = data[3:]
        if busidx in Settings.SynStore.keys():
            dev = 'PV'
            gen_idx = busidx

        elif busidx in Settings.SWStore.keys():
            dev = 'SW'
            gen_idx = busidx

        else:
            raise KeyError

        param = {'bus': busidx,
                 'gen': gen_idx,
                 'type': 0,
                 'AVR': Settings.pss1count,
                 'PSSmodel': 1,
                 'PSSin': 1,
                 'Vmaxsout': EMPTY,
                 'Vminsout': EMPTY,
                 'Kw': EMPTY,  # Stabilizer Gain
                 'Tw': EMPTY,  # Washout Time
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
                 'Ka': EMPTY,  # Gain for additional signal
                 'Ta': EMPTY,  # Time constant for additional signal
                 'Kp': EMPTY,  # Gain for active power
                 'Kv': EMPTY,  # Gain for bus voltage magnitude
                 'Vamax': EMPTY,  # additonal signal(anti-windup)
                 'Vamin': EMPTY,  # additional signal(windup)
                 'Vsmax': EMPTY,  # max output(no additonal)
                 'Vsmin': EMPTY,  # min output(no additional)
                 'FVthresh': EMPTY,
                 'RSthresh': EMPTY,
                 'switch': 1,
                 'status': 1,
                 }

        psatlist = [param['AVR'], param['PSSmodel'], param['PSSin'], param['Vsmax'], param['Vsmin'], param['Kw'],
                    param['Tw'], param['T1'], param['T2'], param['T3'], param['T4'], param['Ka'], param['Ta'],
                    param['Kp'], param['Kv'], param['Vamax'], param['Vamin'], param['Vsmax'], param['Vsmin'],
                    param['FVthresh'], param['RSthresh'], param['switch'], param['status']]

        Settings.Pss.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'DFIG':
        busidx = data[0]
        id = 1      #Id number defaults to 1 for Wind Devices for now
        data = data[2:]
        if busidx in Settings.BusStore.keys():
            pass

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

        Settings.Dfig.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'WTE':
        # Type 1 and 2
        busidx = data[0]
        id = 1
        data = data[2:]
        if busidx in Settings.BusStore.keys():
            pass

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
                    param['delT'], param['c'], param['k'], param['Tsr'], param['Ter'], param['Vwr'],
                    Settings.WindStore[busidx]['H'], param['Tsg'], param['Teg'], param['Vwg'], param['Z0'],
                    param['fstep'], param['nharm']]

        Settings.WindStore[busidx].update(param)
        Settings.Wind.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})


    elif model == 'WTT':
        # Type 1 and 2
        busidx = data[0]
        id = 1
        data = data[3:]
        if busidx in Settings.BusStore.keys():
            pass

        else:
            raise KeyError

        param = {'H': data[0],
                 'Damp': EMPTY,
                 'Htf': EMPTY,
                 'Freq1': EMPTY,
                 'Dshaft': EMPTY
                 }
        psatlist = [param['H'], param['Damp'], param['Htf'], param['Freq1'], param['Dshaft']]
        Settings.WindStore[busidx] = param
        Settings.Wind.append(psatlist)
        Settings.DevicesAtBus[model.lower()].append({'Bus': busidx , 'Id' : id})

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


def init_pf_to_stream(rawfile, dyrfile):
    read(rawfile)
    readadd(dyrfile)
    Settings.nBus = len(Settings.Bus)
    Settings.nLine = len(Settings.Line)
    Settings.Breaker = [19, 8, 100, 345, 60, 1, 6.0, 0, 1, 0]

    # Add PMU(must calculate)
    for bus in range(0, Settings.nBus):
        data = [bus + 2, 0.001, 0.001, 1]
        Settings.Busfreq.append(data)

    for bus in range(0, Settings.nBus - 1):
        data = [bus + 2, Settings.BusStore[bus + 2]['Vn'], 60, 0.05, 0.05, 1, 30, 2, 0]
        Settings.Pmu.append(data)

    Settings.set_sys_params()

    logging.info('PSS/E raw data parsing completed')
    return Settings





