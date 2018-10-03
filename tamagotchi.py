import json
import sys
from datetime import datetime

from sklearn import tree


class Tamagotchi:

    eta = {'eat': 4, 'play': 2, 'poop': 3, 'sleep': 12}
    sleep_time = 6
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

    def asleep(self):
        if ((datetime.now() - self.conf['sleep'][1]).total_seconds() / 60 /
                60) >= self.sleep_time:
            return False
        return True

    def check_status(self):
        if self.asleep():
            return
        for key in self.eta.keys():
            if ((datetime.now() - self.conf[key][1]).total_seconds() / 60 /
                    60) >= self.eta[key]:
                val = 0
                if key == 'poop':
                    val = 1
                self.conf[key] = [val, datetime.now()]
        self.save()

    def run_action(self):
        if self.asleep():
            return self.print_resume(6)
        if self.action == 'e' and self.conf['eat'][0] == 0:
            self.conf['eat'] = [1, datetime.now()]
        elif self.action == 'p':
            self.conf['play'] = [1, datetime.now()]
        elif self.action == 'c':
            self.conf['poop'] = [0, datetime.now()]
        elif self.action == 's':
            self.conf['sleep'] = [1, datetime.now()]
        val = [
            self.conf['eat'][0], self.conf['play'][0], self.conf['poop'][0],
            self.conf['sleep'][0]
        ]
        response = self.model.predict([val])[0]
        if self.action is not 'r':
            self.conf['live'] = self.conf['live'] - 1 if response in [
                0, 1, 2
            ] and self.conf['live'] > 0 else self.conf['live']
            self.conf['live'] = self.conf['live'] + 1 if response in [
                5
            ] and self.conf['live'] < 5 else self.conf['live']
            self.conf['lvl'] = int(
                (datetime.now() - self.conf['start']).total_seconds() / 60 / 60
                / 24)
            if self.conf['live'] == 0:
                print("Game Over")
        self.save()
        self.print_resume(response)

    def print_resume(self, response):
        print("Live {}       Level {}\n             Status {}".format(
            self.conf['live'], self.conf['lvl'], self.status[response]))
        if response in [5, 4]:
            print('''
     .-.
    ( - )
     " "
            ''')
        elif response in [3, 2, 1, 0] and self.conf['poop'][0] == 0:
            print('''
     .-. '
    ( - )
     " "
            ''')
        elif self.conf['poop'][0] == 1:
            print('''
     .-. '   s
    ( - )  S
     " "
            ''')
        elif response in [6]:
            print('''
     _-_   Z
    ( - ) z
     " "
            ''')
        # print(clf.predict_proba([val]))


Tamagotchi()
