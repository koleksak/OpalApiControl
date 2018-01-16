"""User control Threading Events for running simulation interaction"""

import logging
import threading

from run import run_model
import user_settings
start = threading.Event()
stop = threading.Event()
pause = threading.Event()
resume = threading.Event()
end = threading.Event()

pills = [start,stop,pause,resume,end]
