SysPar = {
    # 'Bus': ['V', 'theta', 'P', 'Q', 'w_Busfreq'],
    'Bus': ['w_Busfreq', 'V', 'theta', 'P', 'Q'],
    'Syn': ['p', 'q', 'delta', 'omega','e1d', 'e1q','psid','psiq'],
    'Exc': ['vf', 'vm'],
    'Line': ['Iij', 'Iji', 'Iij_ang', 'Iji_ang'],
    # 'Line': ['Iij', 'Iji', 'Iij_ang', 'Iji_ang', 'Pij', 'Pji', 'Qij', 'Qji', 'Sij', 'Sji'],
    # 'Tg': ['pm', 'wref']
    }


HW_SYNC = 0
SIMULATION = 1
SW_SYNC = 2
NOT_USED = 3
LOW_PRIO_SIM = 4

modelStateList = ["not connected", "not loadable", "compiling", "loadable", "loading",
                  "resetting", "loaded", "paused", "running", "disconnected"]

