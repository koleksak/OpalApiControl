"""Streaming data thread for ePhasorsim using OpalApi Interface"""

from OpalApiControl.OpalApiFormat import stream
from OpalApiControl.OpalApiFormat import psse32
import threading

if __name__ == "__main__":

    SysParam, Varheader, Idxvgs, project, model = psse32.init_pf_to_stream()
    st = threading.Thread(target=stream.ltb_stream_sim, args=(SysParam, Varheader,
                                                              Idxvgs, project, model))
    st.start()
    st.join()