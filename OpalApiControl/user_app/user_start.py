"""User interface object"""
from run import run_model
import threading
import logging
import cmd, sys
import pprint

logging.basicConfig(level=logging.CRITICAL)


class UserApp(cmd.Cmd):
    def __init__(self):
        self.user_settings_file = 'C:/Users/opalrt/repos/OpalApiControl/OpalApiControl/user_app/user_settings'
        self.setting_params = dict()
        self.start = threading.Event()
        self.stop = threading.Event()
        self.pause = threading.Event()
        self.resume = threading.Event()
        self.end = threading.Event()
        self.pills = {'start':self.start, 'stop':self.stop, 'pause':self.pause, 'resume':self.resume, 'end':self.end}
        self.first_start = True

    def settings(self):
        file = open(self.user_settings_file, 'r')
        for num, line in enumerate(file.readlines()):
            line = line.split()
            try:
                self.setting_params[line[0]] = line.pop()
                if line[0] == 'add_power_devs':
                    devs = self.setting_params[line[0]].split(',')
                    self.setting_params['add_power_devs'] = devs
            except:
                pass

    def start_sim(self):

        logging.debug("<initializing simulation run>")
        self.pills['start'].set()


        run = threading.Thread(name='Sim_Start', target=run_model,
                                   kwargs={'project':self.setting_params['project'],
                                           'model':self.setting_params['model'],
                                           'raw':self.setting_params['raw'],
                                           'dyr':self.setting_params['dyr'],
                                           'path':self.setting_params['path'],
                                           'server':self.setting_params['server'],
                                           'add_power_devs':self.setting_params['add_power_devs'],
                                           'pills':self.pills})
        run.setDaemon(True)
        run.start()
        self.first_start = False

    def stop_sim(self):
        logging.debug("<stopping simulation. Notifying acquisition thread to end>")
        self.pills['stop'].set()
        self.pills['start'].clear()

    def pause_sim(self):
        logging.debug("<pausing simulation. Notifying acquisition thread to pause>")
        self.pills['pause'].set()
        self.pills['start'].clear()
        self.pills['stop'].clear()

    def resume_sim(self):
        logging.debug("<resuming simulation. Notifying acquisition thread to start>")
        self.pills['start'].set()
        self.pills['resume'].set()
        self.pills['pause'].clear()
        self.pills['stop'].clear()




app = UserApp()
class UserInterface(cmd.Cmd):
    app.settings()
    intro = 'Opal-RT API Interface.'
    prompt = '({})'.format(app.setting_params['model'])

    def do_start(self,arg):
        """Loads, and Runs simulation for model in user_settings file"""
        if app.first_start:
            logging.info("<starting simulation>")
            app.start_sim()
        else:
            logging.info("<resuming simulation>")
            app.resume_sim()

    def do_settings(self,arg):
        """Shows current file settings in user_settings file"""
        print('******Settings Parameters******')
        for name in app.setting_params:
            print ("Param:{0:15}    Info:{0:10}".format(name,app.setting_params[name]))

    def do_stop(self,arg):
        """Stops running simulation"""
        logging.info("<stopping simulation>")
        app.stop_sim()

    def do_pause(self,arg):
        """Pauses running simulation"""
        logging.info("<pausing simulation>")
        app.pause_sim()

    def do_resume(self,arg):
        """Resumes paused simulation"""
        logging.info("<resuming simulation>")
        app.resume_sim()

    def do_quit(self,arg):
        """Closes User Interface session"""
        #TODO: Make sure RT:lab connection is dismounted properly
        input = raw_input("Quit session? y/n    ")
        input = input.lower()
        if input == 'y':
            self.do_stop("stop")
            sys.exit()
        elif input == 'n':
            pass
        else:
            print("Invalid input")

if __name__ == '__main__':

    UserInterface().cmdloop()
