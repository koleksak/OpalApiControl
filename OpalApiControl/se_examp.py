"""SE example for testing ePhasorsim streaming"""

import OpalApiPy
from OpalApiControl.system import acquire
from OpalApiFormat import stream
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
    JsonSE = json.dumps(SE)
    dimec.send_var('sim', 'SE', JsonSE)

def stream_event_examp():
    Event = {}
    Event['name'] = ['Bus', 'Bus', 'Bus', 'Line', 'Line', 'Line', 'Syn', 'Syn', 'Syn', 'Syn', 'Syn']
    Event['id'] = [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5]
    Event['duration'] = [5, 6, 7, 5, 6, 7, 5, 6, 7, 8, 9]
    Event['action'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Event['time'] = [10, 10, 10, 15, 15, 15, 20, 20, 20, 20, 20]
    global dimec
    JsonEvent = json.dumps(Event)
    dimec.send_var('sim', 'Event', JsonEvent)

if __name__ == '__main__':
    ltb_stream_SE_examp()
    modelstate = acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')
    stream_event_examp()
    while(modelstate == OpalApiPy.MODEL_RUNNING):
        vars = dimec.sync()
        if vars:
            mods = dimec.workspace
            pprint.pprint(mods, None, 1, 40, 10)
        sleep(0.01)
        modelstate, realtimemode = OpalApiPy.GetModelState()



