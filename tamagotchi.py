import json
import sys
from datetime import datetime, timedelta

from sklearn import tree


class Tamagotchi:

    eta = {'eat': 0.75, 'play': 0.41, 'poop': 1, 'sleep': 18}
    sleep_time = 8
    conf = {
        'eat': [0, datetime.now()],
        'play': [0, datetime.now()],
        'poop': [0, datetime.now()],
        'sleep': [1, datetime.now()],
        'live': 5,
        'lvl': 0,
        'start': datetime.now()
    }
    status = ['starving', 'boring', 'tired', 'sad', 'fine', 'happy', 'sleep']

    def __init__(self):
        print("Use (E)at, (P)lay, (C)lean, (S)leep, (R)efresh\n")
        self.load()
        self.model = self.get_model()
        try:
            self.action = sys.argv[1]
        except IndexError:
            self.action = 'r'
        self.check_status()
        self.run_action()

    def load(self):
        try:
            with open('tamagotchi.data') as f:
                self.conf = json.load(f)
            for key in self.eta.keys():
                self.conf[key][1] = datetime.strptime(self.conf[key][1],
                                                      '%Y-%m-%d %H:%M:%S.%f')
            self.conf['start'] = datetime.strptime(self.conf['start'],
                                                   '%Y-%m-%d %H:%M:%S.%f')
        except OSError:
            pass
        except json.decoder.JSONDecodeError:
            pass

    def save(self):
        data = self.conf
        for key in self.eta.keys():
            data[key][1] = data[key][1].__str__()
        data['start'] = data['start'].__str__()
        with open('tamagotchi.data', 'w') as f:
            json.dump(data, f)
        self.load()

    def get_model(self):
        # eat, play, poop, sleep
        x = [[1, 1, 0, 1], [1, 0, 0, 1], [1, 0, 1, 1], [0, 0, 1, 1],
             [0, 0, 1, 0], [0, 0, 1, 0], [1, 1, 0, 0], [1, 0, 0, 0],
             [1, 0, 0, 0], [0, 0, 0, 1], [0, 1, 0, 1]]
        # 5 happy, 4 fine, 3 sad, 2 tired, 1 boring, 0 starving
        y = [5, 4, 3, 3, 3, 1, 2, 2, 1, 0, 0]
        model = tree.DecisionTreeClassifier()
        model = model.fit(x, y)
        return model

    def is_alive(self):
        return self.conf['live'] > 0

    def asleep(self):
        if ((datetime.now() - self.conf['sleep'][1]).total_seconds() / 60 /
                60) >= self.sleep_time or self.conf['sleep'][0] == 0:
            return False
        return True

    def check_status(self):
        for key in self.eta.keys():
            if ((datetime.now() - self.conf[key][1]).total_seconds() / 60 /
                    60) >= self.eta[key]:
                val = 0
                if key == 'poop':
                    val = 1
                self.conf[key] = [val, datetime.now()]
        if not self.asleep() and self.is_alive():
            self.save()

    def try_to_wake_up(self):
        if self.asleep() and self.is_alive():  # Try to wake up
            if self.action == 'e' and self.conf['eat'][0] == 0:
                self.conf['sleep'] = [
                    1, datetime.now() - timedelta(hours=self.sleep_time)
                ]
                self.save()
                return True
        if not self.asleep() and self.is_alive():
            return True
        return False

    def prepare_val(self):
        actions = {
            'e': ('eat', 1),
            'p': ('play', 1),
            'c': ('poop', 0),
            's': ('sleep', 1)
        }
        action_val = actions.get(self.action, None)
        if action_val:
            accept_action = True
            if action_val[0] == 'eat' and self.conf['eat'][0] > 0:
                accept_action = False
            if accept_action:
                self.conf[action_val[0]] = [action_val[1], datetime.now()]
        return [
            self.conf['eat'][0], self.conf['play'][0], self.conf['poop'][0],
            self.conf['sleep'][0]
        ]

    def update_live_and_lvl(self, response):
        if self.action is not 'r':
            self.conf['live'] = self.conf['live'] - 1 if response in [
                0, 1, 2, 3
            ] and self.conf['live'] > 0 else self.conf['live']
            self.conf['live'] = self.conf['live'] + 1 if response in [
                5
            ] and self.conf['live'] < 5 else self.conf['live']
            self.conf['lvl'] = int(
                (datetime.now() - self.conf['start']).total_seconds() / 60 / 60
                / 24)

    def run_action(self):
        if not self.try_to_wake_up():
            return self.print_resume(6)
        val = self.prepare_val()
        if not self.asleep():
            response = self.model.predict([val])[0]
        else:
            self.action = 'r'
            response = 6
        self.update_live_and_lvl(response)
        self.save()
        self.print_resume(response)

    def print_resume(self, response):
        print("Live {}       Level {}\n             Status {}".format(
            self.conf['live'], self.conf['lvl'], self.status[response]))
        if self.conf['live'] <= 0:
            print("Game Over")
            print(self.screen['dead'])
        elif response in [5]:
            print(self.screen['happy'])
        elif response in [4]:
            print(self.screen['normal'])
        elif response in [3, 2, 1, 0] and self.conf['poop'][0] == 0:
            print(self.screen['bad'])
        elif response in [6]:
            print(self.screen['sleep'])
        elif self.conf['poop'][0] == 1:
            print(self.screen['dirty'])

    screen = {
        'normal': '''
     .-.
    ( - )
     " "
              ''',
        'happy': '''
      _
    (^-^)
     " "
              ''',
        'bad': '''
     .-. '
    ( - )
     " "
              ''',
        'sleep': '''
     _-_   Z
    ( - ) z
     " "
              ''',
        'dirty': '''
     .-. '   s
    ( - )  S
     " "
              ''',
        'dead': '''
     _|_
   ,,,|,,,
              '''
    }


Tamagotchi()
