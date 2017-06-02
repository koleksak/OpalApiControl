"""Creates SysParam and varvgs subsets per device requests"""

import OpalApiControl
import dime
import psse32
import stream
import idxvgs
import logging

Vgsmodidx = {}

def mod_requests():

    if(stream.dimec.sync):

        dev_list = stream.dimec.get_devices.response
        for idx in range(1,len(dev_list)):
            dev_name = str(dev_list[idx])
            if dev_name == 'sim':
                continue

            if(dev_name):
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
                    SysParam = {}
                    SysName = {}

                    for dev in param:
                        SysParam = []
