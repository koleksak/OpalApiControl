"""User interface object"""
from run import run_model
import threading
import logging
import cmd, sys
from time import sleep

logging.basicConfig(level=logging.DEBUG)


class UserApp(cmd.Cmd):
    def __init__(self):
        self.user_settings_file = 'C:/Users/opalrt/repos/OpalApiControl/OpalApiControl/user_app/user_settings'
        self.setting_params = dict()
        self.start = threading.Event()
        self.stop = threading.Event()
        self.pause = threading.Event()
        self.resume = threading.Event()
        self.end = threading.Event()
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.loaded_sim = threading.Condition()
        self.pills = {'start':self.start, 'stop':self.stop, 'pause':self.pause, 'resume':self.resume,
                      'end':self.end, 'lock':self.lock,
                      'condition':self.condition, 'loaded':self.loaded_sim}
        self.run = None

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

    def initialize_sim(self):
        logging.debug("<initializing simulation thread>")
        run = threading.Thread(name='Sim_Start', target=run_model,
                               kwargs={'project': self.setting_params['project'],
                                       'model': self.setting_params['model'],
                                       'raw': self.setting_params['raw'],
                                       'dyr': self.setting_params['dyr'],
                                       'path': self.setting_params['path'],
                                       'server': self.setting_params['server'],
                                       'add_power_devs': self.setting_params['add_power_devs'],
                                       'pills': self.pills})
        return run

    def start_sim(self):
        self.run = self.initialize_sim()
        logging.debug("<starting simulation>")
        self.run.setDaemon(True)
        self.run.start()
        # sleep(30)
        while not self.pills['start'].isSet():
            self.pills['loaded'].acquire()
            logging.debug("<set start waiting>")
            self.pills['loaded'].wait()
            logging.debug("<start setting>")
            self.pills['start'].set()
            sleep(3)
            self.pills['condition'].acquire()
            self.pills['condition'].notifyAll()
            self.pills['condition'].release()
            self.pills['loaded'].release()

    def stop_sim(self):
        logging.debug("<setting stop simulation pills>")
        self.pills['lock'].acquire()
        self.pills['stop'].set()
        self.pills['start'].clear()
        self.pills['lock'].release()
        sleep(1)
        self.pills['condition'].acquire()
        self.pills['condition'].notifyAll()
        self.pills['condition'].release()

    def pause_sim(self):
        logging.debug("<setting pause simulation pills>")
        self.pills['lock'].acquire()
        self.pills['pause'].set()
        self.pills['start'].clear()
        self.pills['stop'].clear()
        self.pills['lock'].release()

    def resume_sim(self):
        logging.debug("<setting resume simulation pills>")
        self.pills['lock'].acquire()
        self.pills['condition'].acquire()
        self.pills['start'].set()
        self.pills['resume'].set()
        self.pills['pause'].clear()
        self.pills['stop'].clear()
        self.pills['lock'].release()
        self.pills['condition'].notifyAll()
        self.pills['condition'].release()
        sleep(2)

app = UserApp()
class UserInterface(cmd.Cmd):
    app.settings()
    intro = 'Opal-RT API Interface.'
    prompt = '({})'.format(app.setting_params['model'])

    def do_start(self,arg):
        """Loads, and Runs simulation for model in user_settings file"""
        logging.info("<starting simulation>")
        app.start_sim()

    def do_settings(self,arg):
        """Shows current file settings in user_settings file"""
        print('******Settings Parameters******')
        for param, name in app.setting_params.items():
            print ("Param:{0:15}    Info:{1:10} ".format(param, name))

    def do_stop(self,arg):
        """Stops running simulation"""
        logging.info("<stopping simulation>")
        app.stop_sim()

    def do_pause(self,arg):
        """Pauses running simulation"""
        logging.info("<pausing simulation>")
        app.pause_sim()
        sleep(2)

    def do_resume(self,arg):
        """Resumes paused simulation"""
        logging.info("<resuming simulation>")
        app.resume_sim()
        sleep(2)

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
