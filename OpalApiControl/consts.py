SysPar = {
    # 'Bus': ['V', 'theta', 'P', 'Q', 'w_Busfreq'],
    'Bus': ['V', 'theta'],
    'Syn': ['p', 'q', 'delta', 'omega','e1d', 'e1q','psid','psiq'],
    'Exc': ['vf', 'vm'],
    'Line' : ['Iij', 'Iji'],
    # 'Line': ['Pij', 'Pji', 'Qij', 'Qji', 'Iij', 'Iji', 'Sij', 'Sji'],
    # 'Tg': ['pm', 'wref']
    }

HW_SYNC = 0
SIMULATION = 1
SW_SYNC = 2
NOT_USED = 3
LOW_PRIO_SIM = 4

modelStateList = ["not connected", "not loadable", "compiling", "loadable", "loading",
                  "resetting", "loaded", "paused", "running", "disconnected"]

