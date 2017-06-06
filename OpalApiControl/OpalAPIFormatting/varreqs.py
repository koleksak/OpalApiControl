"""Creates SysParam and varvgs subsets per device requests"""

import OpalApiControl
import dime
import psse32
import stream
import idxvgs
import logging

Vgsinfo = {}
SysParam = {}
SysName = {}


def mod_requests():

    if stream.dimec.sync:

        dev_list = stream.dimec.get_devices.response
        Vgsinfo['dev_list'] = dev_list
        for idx in range(1, len(dev_list)):
            dev_name = str(dev_list[idx])
            if dev_name == 'sim':
                continue

            if dev_name:
                param, vgsvaridx, usepmu, limitsample = []

                try:
                    param = dev_name + '.param'

                except:
                    logging.error('<Param Field Error for {}>'.format(dev_name))

                try:
                    vgsvaridx = dev_name + '.vgsvaridx'

                except:
                    logging.error('<Vgsvaridx Field Error for {}>'.format(dev_name))

                try:
                    usepmu = dev_name + '.usepmu'

                except:
                    logging.error('<Usepmu Field Error for {}>'.format(dev_name))

                try:
                    limitsample = dev_name + '.limitsample'

                except:
                    logging.error('<Limitsample Field Error for {}>'.format(dev_name))

                if (len(param) & len(vgsvaridx)) == 0:
                    logging.error('<No Param and Var data requested')
                    break

                #Send Parameter data
                if len(param) != 0:

                    for dev in param:
                        if dev ==('Pmu' or 'Exc' or 'Pss' or 'Dfig' or 'Syn'):
                            SysParam[dev] = dev + '.con'
                        else:
                            SysParam[dev] = dev + '.store'

                        if dev == ('Bus' or 'Areas' or 'Regions'):
                            SysName[dev] = dev + '.names'

                    SysParam['nBus'] = len(psse32.SysParam['Bus'])
                    SysParam['nLine'] = len(psse32.SysParam['Line'])

                    stream.dimec.send_var(dev, 'SysParam')
                    stream.dimec.send_var(dev_name, 'SysName')

                if len(vgsvaridx) != 0:
                    if 'location' not in Vgsinfo:
                        if len(vgsvaridx) == 0:
                            Vgsinfo['location'] = []
                            Vgsinfo['var_idx'] = list(vgsvaridx)
                            Vgsinfo['usepmu'] = list(usepmu)
                            Vgsinfo['limitsample'] = list(limitsample)

                        else:
                            Vgsinfo['location'].append(vgsvaridx)
                            Vgsinfo['var_idx'].append(usepmu)
                            Vgsinfo['limitsample'].aooend(limitsample)

                dev_name['param'] = []
                dev_name['vgsvaridx'] = []
                dev_name['usepmu'] = []
                dev_name['limitsample'] = []