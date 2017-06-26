"""SE example for testing ePhasorsim streaming"""
import dime
from dime import dime
import OpalApiPy
import RtlabApi
from OpalApiControl.system import acquire
from OpalApiFormat import idxvgs
from OpalApiFormat import varreqs
from OpalApiFormat import stream
import logging
import json
from time import sleep
import pprint


def ltb_stream_SE_examp():
    SE = {}
    SE['param'] = ['Bus', 'Line', 'PV', 'PQ']
    SE['vgsvaridx'] = list(range(0, 5))
    SE['usepmu'] = 1
    SE['limitsample'] = 1
    global dimec
    dimec = stream.set_dime_connect('SE', 'tcp://127.0.0.1:5678')
    #idxvgs.send_varhead_idxvgs('sim', dimec)
    JsonSE = json.dumps(SE)
    dimec.send_var('sim', 'SE', JsonSE)
    #dimec.exit()
    #varreqs.mod_requests()
    #stream.ltb_stream()
    #acquire.connectToModelTest('IEEE39Acq', 'phasor01_IEEE39')
    #dimec.send_var('sim', 'SE', JsonSE)


if __name__ == '__main__':
    ltb_stream_SE_examp()
    modelstate = acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')
    while(modelstate == OpalApiPy.MODEL_RUNNING):
        vars = dimec.sync()
        if vars:
            mods = dimec.workspace
            pprint.pprint(mods['Varvgs'],None, 1, 40, 10)
        sleep(0.03333)
        modelstate, realtimemode = OpalApiPy.GetModelState()

    #groups = (1, 2, 3, 4)
    #stream.stream_data(groups)


