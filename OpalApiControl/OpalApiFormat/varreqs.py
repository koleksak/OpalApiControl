"""Creates SysParam and varvgs subsets per device requests"""

import dime
import psse32
import stream
import idxvgs
import logging
import json
import unicodedata
from pymatbridge import Matlab

Vgsinfo = {}
Vgsinfo['dev_list'] = {}
SysParam = {}
SysName = {}
prereq = 'sim'

def mod_requests():
    varname = stream.dimec.sync()
    if varname:
        modules = stream.dimec.workspace
        #modules = json.loads(modules)
        global Vgsinfo
        Vgsinfo['dev_list'] = modules
        #print('MODULES'.format(modules))
        #print('Vgsinfo', Vgsinfo)
        if prereq not in Vgsinfo['dev_list'].keys():
            print prereq
            logging.error('<No simulator connected>')

        else:
            for dev_name in stream.dimec.workspace:
                if dev_name == 'sim':
                    continue
                jsonmods = Vgsinfo['dev_list'][dev_name]
                mods = json.loads(jsonmods)
                Vgsinfo['dev_list'][dev_name] = mods

                if dev_name:
                    param, vgsvaridx, usepmu, limitsample = ([], [], [], [])

                    try:
                        param = Vgsinfo['dev_list'][dev_name]['param']


                    except:
                        logging.error('<Param Field Error for {}>'.format(dev_name))

                    try:
                        vgsvaridx = Vgsinfo['dev_list'][dev_name]['vgsvaridx']

                    except:
                        logging.error('<Vgsvaridx Field Error for {}>'.format(dev_name))

                    try:
                        usepmu = Vgsinfo['dev_list'][dev_name]['usepmu']

                    except:
                        logging.error('<Usepmu Field Error for {}>'.format(dev_name))

                    try:
                        limitsample = Vgsinfo['dev_list'][dev_name]['limitsample']

                    except:
                        logging.error('<Limitsample Field Error for {}>'.format(dev_name))

                    if (len(param) == 0) & (len(vgsvaridx) == 0):
                        logging.error('<No Param and Var data requested')
                        break

                    #Send Parameter data
                    if len(param) != 0:
                        for dev in param:

                            #print param
                            if dev == ('Pmu' or 'Exc' or 'Pss' or 'Dfig' or 'Syn'):
                                SysParam[dev] = Vgsinfo['dev_list']['sim']['SysParam'][dev]
                            else:
                                SysParam[dev] = Vgsinfo['dev_list']['sim']['SysParam'][dev]

                            if dev == ('Bus' or 'Areas' or 'Regions'):
                                SysName[dev] = Vgsinfo['dev_list']['sim']['SysParam'][dev]

                        SysParam['nBus'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Bus'])
                        SysParam['nLine'] = len(Vgsinfo['dev_list']['sim']['SysParam']['Line'])
                        JsonSysParam = json.dumps(SysParam)
                        JsonSysName = json.dumps(SysName)
                        stream.dimec.send_var(dev_name, 'SysParam', JsonSysParam)
                        stream.dimec.send_var(dev_name, 'SysName', JsonSysName)
                        print('Sent SysParam and SysName to {}'.format(dev_name))

                    if len(vgsvaridx) != 0:
                        if 'location' not in Vgsinfo:
                            Vgsinfo[dev_name] = {}
                            print('Create vgs dev', Vgsinfo)
                            Vgsinfo['dev_list'][dev_name]['location'] = []
                            Vgsinfo['dev_list'][dev_name]['vgsvaridx'] = vgsvaridx
                            Vgsinfo['dev_list'][dev_name]['usepmu'] = usepmu
                            Vgsinfo['dev_list'][dev_name]['limitsample'] = limitsample

                        else:
                            Vgsinfo['dev_list'].append(dev_name)
                            #Vgsinfo[dev_name]['location'].append(vgsvaridx)
                            Vgsinfo['dev_list'][dev_name]['vgsvaridx'].append(vgsvaridx)
                            Vgsinfo['dev_list'][dev_name]['usepmu'] = usepmu
                            Vgsinfo['dev_list'][dev_name]['limitsample'].append(limitsample)

                    #Vgsinfo[dev_name]['param'] = []
                    #Vgsinfo[dev_name]['vgsvaridx'] = []
                    #Vgsinfo[dev_name]['usepmu'] = []
                    #Vgsinfo[dev_name]['limitsample'] = []
    #print Vgsinfo
    return Vgsinfo

def obj_to_dict_helper(objects):
    """Strips unicode formatting from JSON objects to convert to Python ascii Dictionary"""
    dict_names_list = []
    for obj in objects:
        obj = unicodedata.normalize('NFKD', obj).encode('ascii', 'ignore')
        dict_names_list.append(obj)
    return dict_names_list

