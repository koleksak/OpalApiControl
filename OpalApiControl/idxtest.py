from OpalApiControl.signals import signalcontrol
from OpalApiControl.system import acquire
from OpalApiControl.OpalApiFormat import idxvgs



if __name__ == '__main__':
    acquire.connectToModel('IEEE39Acq', 'phasor01_IEEE39')
    idxvgs.set_ephasor_ports()