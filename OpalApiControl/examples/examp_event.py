from dime import dime


dimec = dime.Dime('mod1', 'tcp://127.0.0.1:5678')
dimec.start()


Event = dict()
Event['name'] = ['Bus', 'Bus', 'Bus', 'Line', 'Line', 'Line', 'Syn', 'Syn', 'Syn', 'Syn', 'Syn']
Event['id'] = [1, 2, 3, 1, 2, 3, 1, 2, 3, 4, 5]
Event['duration'] = [0.2, 0.3, 0.4, 0.1, 0.2, 0.3, 1, 1, 1 , 1, 1]
Event['action'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
Event['time'] = [2, 2, 2, 1, 3, 3, 5, 5, 5, 5, 5]
# Event['name'] = ['Bus']
# Event['id'] = [1]
# Event['duration'] = [5]
# Event['action'] = [0]
# Event['time'] = [10]


if __name__ == '__main__':
    dimec.send_var('sim', 'Event', Event)
    dimec.exit
