#!/usr/bin/env python3

"""
Isthmus Cyclicus Crypticus

"""

import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Agent():
    def __init__(self, name='Anonymous', assignment=None):
        self.name = name
        self.assignment = assignment
        self.wait = False
        self.X = [0]
        self.Y = [0]
        self.Z = [0]
        self.pos = [0, 0, 0]
        self.face = [0, 0, 0]

    def move(self, d):
        if d is True:
            return None
        # d, 3d vector to move
        self.face = d
        self.pos = [self.pos[0] + d[0], self.pos[1] + d[1], self.pos[2] + d[2]]
        self.X.append(self.pos[0])
        self.Y.append(self.pos[1])
        self.Z.append(self.pos[2])
        return self.pos

    def listen(self, d):
        if d == []:
            self.wait = True
        for m in d:
            if self.wait:
                self.go()
            if self.move(m) is None:
                return None
        return True

    def go(self):
        self.say('''Green light, go.
  Red light, stop.
  Green light, stop.
  Red light, go!''')
        self.wait = False

    def path(self):
        return self.X, self.Y, self.Z

    def say(self, t):
        print(f'{self.name}: {t}')


class Translator(Agent):
    TRANSLITERATION = 'NESWUDLRtfneswudHX'
    SCALOTI_LOW     = 'ᐃᐅᐁᐊᑎᑌᒣᒥᒋᑊᐱᐳᐯᐸᑭᑯᐦᕽ'
    NUMERALS        = '౦୧౨୩౪୫౬୭౮୯'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = 0
        print(self.assignment)
        print('Transliterating:')
        print(self.transliterate(self.assignment))
        self.assignment = self.transliterate(self.assignment).strip().split('\n')

    def translate(self, guards):
        instructions = self.assignment[self.current]
        self.current = (self.current + 1) % len(self.assignment)
        if guards.alert(self.path()):
            self.say('Wait...')
            return []
        maxeast = sum([ins.count('E') for ins in self.assignment])
        if guards.pos > (self.pos[1] + maxeast):
            self.say('The guards have overrun the Crypticus. We have to abort the mission. Pull out!')
            return[True]
        # return instruction
        absolute = {
                'N': [-1, 0, 0],
                'S': [1, 0, 0],
                'E': [0, 1, 0],
                'W': [0, -1, 0],
                'U': [0, 0, 1],
                'D': [0, 0, -1],
        }
        directions = {
                'N': 'north',
                'S': 'south',
                'E': 'east',
                'W': 'west',
                'U': 'up',
                'D': 'down',
        }

        i = 0
        movements = []
        current_directions = []
        while i < len(instructions):
            m = None
            c = instructions[i]
            if c in absolute.keys():
                d = absolute[c]
                n = i + 1
                final_dir = directions[c]
                while n < len(instructions) and instructions[n] in ''.join(absolute.keys()).lower():
                    mod = absolute[instructions[n].upper()]
                    d = [d[x] + mod[x] for x in (0, 1, 2)]
                    final_dir += '-' + directions[instructions[n].upper()]
                    n += 1
                m = [d[x]/(max(1, n-i-1)) for x in (0, 1, 2)]
                current_directions.append('Go %s.' % final_dir)
            elif c == 't':
                current_directions.append('Take the next sharp turn to double back the way you came.')
                m = [-1 * v for v in self.face]
            elif c == 'f':
                current_directions.append('Continue onward.')
                m = self.face
            elif c == 'H':  # hide
                current_directions.append('Avoid the main concourse.')
                m = [0.01, 0, 0]
            elif c == 'X':
                current_directions.append('You should be able to see a red door to your right with a green frame.')
                m = True 
            if m:
                movements.append(m)
                self.move(m)
            i += 1
        self.say(' '.join(current_directions))
        return movements

    def transliterate(self, t):
        for i,c in enumerate(self.TRANSLITERATION):
            t = t.replace(self.SCALOTI_LOW[i], c)
        return t

    def to_scaloti(self, t):
        for i,c in enumerate(self.TRANSLITERATION):
            t = t.replace(c, self.SCALOTI_LOW[i])
        return t


class Guards():
    def __init__(self):
        self.pos = 0

    def advance(self):
        self.pos += 1

    def alert(self, path):
        x, y, z = path
        if len(x) > self.pos:
            return x[self.pos] == 0

    def locations(self):
        # returns X, Y, Z scatter plot locations
        return [0] * self.pos, list(range(self.pos)), 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('instructions', help='Instructions for reaching a goal, written in Scaloti Abbreviated-Low Breen.')
    parser.add_argument('--agent', '-a', help='Name of the active agent.', default='Æon')
    parser.add_argument('--translator', '-t', help='Name of the translating agent.', default='Una')
    args = parser.parse_args()

    fname = args.instructions

    with open(fname, 'r') as f:
        code = f.read()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Assign Agents
    agent = Agent(args.agent, assignment=code)
    translator = Translator(args.translator, assignment=agent.assignment)

    guards = Guards()
    limit = 1000
    i = 0
    while agent.listen(translator.translate(guards)) and limit and i < limit:
        guards.advance()
        i += 1

    agx, agy, agz = agent.path()
    ax.plot(agx, agy, agz, color='m', label=f'Agent route ({agent.name})')

    # Guards
    gx, gy, gz = guards.locations()
    ax.scatter(gx, gy, zs=gz, zdir='z', c='r', label='Guards')

    # Isthmus
    xs = [-2, -1, 0, 1, 2]
    ys = [0, 0, max(agy + gy), 0, 0]
    ax.bar(xs, ys, zs=0, zdir='z', color='c', alpha=0.8, label='Isthmus')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Level')
    #ax.set_xlim(-10, 10)
    #ax.set_ylim(0, 20)
    ax.set_zlim(-20, 10)
    ax.legend()
    plt.show()
