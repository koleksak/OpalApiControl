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
    SE['vgsvaridx'] = list(range(0, 10000))
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
    Event['duration'] = [0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 1, 1, 1 , 1, 1]
    Event['action'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    Event['time'] = [2, 2, 2, 3, 3, 3, 5, 5, 5, 5, 5]
    # Event['name'] = ['Bus']
    # Event['id'] = [1]
    # Event['duration'] = [5]
    # Event['action'] = [0]
    # Event['time'] = [10]

    global dimec
    JsonEvent = json.dumps(Event)
    dimec.send_var('sim', 'Event', JsonEvent)

if __name__ == '__main__':
    modelstate = acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')
    ltb_stream_SE_examp()
    stream_event_examp()
    while(modelstate == OpalApiPy.MODEL_RUNNING):
    # while(True):
        vars = dimec.sync(1)
        if vars:
            mods = dimec.workspace
            #pprint.pprint(mods, None, 1, 40, 10)
        sleep(0.01)
        modelstate, realtimemode = OpalApiPy.GetModelState()
    dimec.exit()



