from run import run_model
import logging
import threading

logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    localhost = 'tcp://127.0.0.1:5678'
    cui_aw = 'tcp://10.129.132.192:9999'
    cui = 'tcp://160.36.59.189:5000'
    # run_model(project='WECC181', model='phasor03_PSSE', raw='Curent02_final_ConstZCoords.raw', dyr='Curent02_final.dyr',
    #           path='C:/RT-LABv11_Workspace_New/', server=localhost)
    project = 'WECC181'
    model = 'phasor03_PSSE'
    raw = 'Curent02_final_ConstZCoords.raw'
    dyr = 'Curent02_final.dyr'
    path='C:/RT-LABv11_Workspace_New/'
    server=localhost
    add_power_devs= None

    run = threading.Thread(name='Run', target=run_model,kwargs={'project':project, 'model':model, 'raw':raw, 'dyr':dyr,
               'path':path,'server':server,'add_power_devs':add_power_devs})

    run.setDaemon(True)
    run.start()
    logging.info("Run Started")
