"""Creates SysParam and varvgs subsets per device requests"""

import stream
import logging
import json
import unicodedata


Vgsinfo = {}
SysParam = {}
SysName = {}
prereq = 'sim'

def mod_requests(SysParamInf):
    varname = stream.dimec.sync()
    dev_list = stream.dimec.get_devices()

    if varname:
        modules = stream.dimec.workspace
        global Vgsinfo
        Vgsinfo['dev_list'] = {}
        if prereq not in dev_list:
            print prereq
            logging.error('<No simulator connected>')

        else:
            for dev_name in dev_list:
                if dev_name == 'sim':
                    continue
                jsonmods = modules[dev_name]
                modules[dev_name] = json.loads(jsonmods)

                if dev_name:
                    param, vgsvaridx, usepmu, limitsample = ([], [], [], [])

                    try:
                        #param = Vgsinfo['dev_list'][dev_name]['param']
                        param = modules[dev_name]['param']


                    except:
                        logging.error('<Param Field Error for {}>'.format(dev_name))

                    try:
                        #vgsvaridx = Vgsinfo['dev_list'][dev_name]['vgsvaridx']
                        vgsvaridx = modules[dev_name]['vgsvaridx']

                    except:
                        logging.error('<Vgsvaridx Field Error for {}>'.format(dev_name))

                    try:
                        #usepmu = Vgsinfo['dev_list'][dev_name]['usepmu']
                        usepmu = modules[dev_name]['usepmu']

                    except:
                        logging.error('<Usepmu Field Error for {}>'.format(dev_name))

                    try:
                        #limitsample = Vgsinfo['dev_list'][dev_name]['limitsample']
                        limitsample = modules[dev_name]['limitsample']

                    except:
                        logging.error('<Limitsample Field Error for {}>'.format(dev_name))

                    if (len(param) == 0) & (len(vgsvaridx) == 0):
                        logging.error('<No Param and Var data requested')
                        break

                    #Send Parameter data
                    if len(param) != 0:
                        for dev in param:
                            if dev == ('BusNames' or 'Areas' or 'Regions'):
                                if dev == 'BusNames':
                                    dev = 'Bus'
                                SysName[dev] = SysParamInf[dev]
                            else:
                                #SysParam[dev] = Vgsinfo['dev_list']['sim']['SysParam'][dev]
                                SysParam[dev] = SysParamInf[dev]

                        #SysParam['nBus'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Bus'])
                        SysParam['nBus'] = len(SysParamInf['Bus'])
                        #SysParam['nLine'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Line'])
                        SysParam['nLine'] = len(SysParamInf['Line'])
                        JsonSysParam = json.dumps(SysParam)
                        JsonSysName = json.dumps(SysName)
                        stream.dimec.send_var(dev_name, 'SysParam', JsonSysParam)
                        stream.dimec.send_var(dev_name, 'SysName', JsonSysName)
                        print('Sent SysParam and SysName to {}'.format(dev_name))

                    if len(vgsvaridx) != 0:
                        if dev_name not in Vgsinfo['dev_list']:
                            keys = Vgsinfo['dev_list'].keys()
                            keys.append(dev_name)
                            Vgsinfo[dev_name] = {}
                            Vgsinfo['dev_list'] = keys
                            #Vgsinfo[dev_name]['location'] = []
                            Vgsinfo[dev_name]['vgsvaridx'] = vgsvaridx
                            Vgsinfo[dev_name]['usepmu'] = usepmu
                            Vgsinfo[dev_name]['limitsample'] = limitsample

                        else:
                            #Vgsinfo['dev_list'].append(dev_name+1)
                            Vgsinfo[dev_name]['vgsvaridx'].append(vgsvaridx)
                            Vgsinfo[dev_name]['usepmu'].append(usepmu)
                            Vgsinfo[dev_name]['limitsample'].append(limitsample)

                    modules[dev_name]['param'] = []
                    modules[dev_name]['vgsvaridx'] = []
                    modules[dev_name]['usepmu'] = []
                    modules[dev_name]['limitsample'] = []

    return Vgsinfo


def obj_to_dict_helper(objects):
    """Strips unicode formatting from JSON objects to convert to Python ascii Dictionary"""
    dict_names_list = []
    for obj in objects:
        obj = unicodedata.normalize('NFKD', obj).encode('ascii', 'ignore')
        dict_names_list.append(obj)
    return dict_names_list

