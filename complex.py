#!/usr/bin/env python3

"""
Isthmus Cyclicus Crypticus

"""

import argparse
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


DEBUG = False


class Agent():
    def __init__(self, name='Anonymous', assignment=None):
        self.name = name
        self.assignment = assignment
        self.wait = False
        self.pos = [0, 0, -1]
        self.X, self.Y, self.Z = [[v] for v in self.pos]
        self.face = [0, 1, 0]
        self.success = False

    def move(self, d):
        if isinstance(d, bool):
            # Target reached, or Crypticus overrun.
            self.success = d
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
            if m and self.wait:
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = 0
        print(self.assignment)
        print('Transliterating:')
        print(self.transliterate(self.assignment))
        self.assignment = self.transliterate(self.assignment).strip().split('\n')

    def abs_dir(self, i, instructions):
        if DEBUG:
            print('DEBUG:', i, instructions)
        c = instructions[i]
        d = self.absolute[c]
        n = i + 1
        final_dir = self.directions[c]
        while n < len(instructions) and instructions[n] in ''.join(self.absolute.keys()).lower():
            mod = self.absolute[instructions[n].upper()]
            d = [d[x] + mod[x] for x in (0, 1, 2)]
            final_dir += f'-{self.directions[instructions[n].upper()]}'
            n += 1
        m = [d[x] / (max(1, n - i - 1)) for x in (0, 1, 2)]
        if 'up-' in final_dir:
            final_dir = f'Ascend {final_dir}.'.replace('up-', '', 1).replace('up-', 'steeply ', 1).replace('.', 'ward.')
        elif 'down-' in final_dir:
            final_dir = f'Descend {final_dir}.'.replace('down-', '', 1).replace('down-', 'steeply ', 1).replace('.', 'ward.')
        else:
            final_dir = f'Go {final_dir}.'
        return final_dir, m

    def combine(self, commands):
        """
        Combine a series of commands into natural sentences.
        """
        # TODO: flesh this out!
        if self.wait:
            commands = ["Ok, it's safe to move!"] + commands
            self.wait = False
        return ' '.join(commands)

    def translate(self, guards):
        instructions = self.assignment[self.current]
        self.current = (self.current + 1) % len(self.assignment)
        if guards.alert(self.path()):
            self.say('Wait...')
            self.wait = True
            return []
        maxeast = sum([ins.count('E') for ins in self.assignment])
        if guards.pos > (self.pos[1] + maxeast):
            self.say('The guards have overrun the Crypticus. We have to abort the mission. Pull out!')
            return [False]

        i = 0
        movements = []
        current_directions = []
        while i < len(instructions):
            m = None
            c = instructions[i]
            if c in self.absolute.keys():
                command, m = self.abs_dir(i, instructions)
                current_directions.append(command)
            elif c == 'L':
                current_directions.append('Turn left.')
                m = [-1 * self.face[1], self.face[0], self.face[2]]
            elif c == 'R':
                current_directions.append('Turn right.')
                m = [self.face[1], -1 * self.face[0], self.face[2]]
            elif c == 't':
                #current_directions.append('Take the next sharp turn to double back the way you came.')
                #current_directions.append('Take the switchback, reversing your course.')
                #current_directions.append('Reverse course by taking the switchback.')
                current_directions.append('Take the switchback.')
                m = [-1 * v for v in self.face]
            elif c == 'f':
                #current_directions.append('Continue onward.')
                #current_directions.append('Keep going.')
                current_directions.append('Press on.')
                m = self.face
            elif c == 'H':  # hide
                current_directions.append('Avoid the main concourse.')
                m = [0.01, 0, 0]
            elif c == 'X':
                current_directions.append('You should be able to see a red door to your right... with a green frame.')
                m = True
            if m:
                movements.append(m)
                self.move(m)
            i += 1
        self.say(self.combine(current_directions))
        return movements

    def transliterate(self, t):
        for i, c in enumerate(self.TRANSLITERATION):
            t = t.replace(self.SCALOTI_LOW[i], c)
        return t

    def to_scaloti(self, t):
        for i, c in enumerate(self.TRANSLITERATION):
            t = t.replace(c, self.SCALOTI_LOW[i])
        return t


class Guards():
    def __init__(self):
        self.pos = 0

    def act(self, s):
        print(' { ' + s + ' }')

    def advance(self):
        #self.act('The guards advance')
        self.pos += 1

    def alert(self, path):
        x, y, z = path
        if len(x) > self.pos:
            if x[self.pos] == 0:
                self.act('The guards crossing the isthmus above are on high alert!')
            return x[self.pos] == 0

    def locations(self):
        # returns X, Y, Z scatter plot locations
        return [0] * self.pos, list(range(self.pos)), 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('instructions', help='Instructions for reaching a goal, written in Scaloti Abbreviated-Low Breen.')
    parser.add_argument('--agent', '-a', help='Name of the active agent.', default='Æon')
    parser.add_argument('--translator', '-t', help='Name of the translating agent.', default='Una')
    parser.add_argument('--limit', '-l', help='Limit mission to {limit} steps. 0 = no limit.', type=int, default=0)
    parser.add_argument('--debug', '-d', help='Debug', action='store_true')
    args = parser.parse_args()

    fname = args.instructions
    limit = args.limit
    DEBUG = args.debug

    with open(fname, 'r') as f:
        code = f.read()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Assign Agents
    agent = Agent(args.agent, assignment=code)
    translator = Translator(args.translator, assignment=agent.assignment)

    guards = Guards()
    steps = 0

    if limit:
        agent.say(f"All right, make this an impeccable rush job. Let's keep it to {limit} passages.")
    while agent.listen(translator.translate(guards)) and (not limit or steps < limit):
        guards.advance()
        steps += 1

    # Plot result:
    # Agent
    agx, agy, agz = agent.path()
    ax.plot(agx, agy, agz, color='m', label=f'Agent route ({agent.name})')

    # Guards
    gx, gy, gz = guards.locations()
    ax.scatter(gx, gy, zs=gz, zdir='z', c='r', alpha=0.8, label='Guards')

    # Isthmus
    xs = [-2, -1, 0, 1, 2]
    ys = [0, 0, max(agy + gy), 0, 0]
    ax.bar(xs, ys, zs=0, zdir='z', color='c', alpha=0.3, label='Isthmus')

    # Green framed door, if target reached.
    if agent.success:
        ax.plot(agx[-1], agy[-1], agz[-1], 'gs', fillstyle='none', label='Target chamber')
        print(f'\nMission successfully completed after {steps} passages.')
    elif not limit or steps < limit:
        print(f'\nMission failed after {steps} passages.')
    elif limit:
        print(f'....\nMission aborted at limit = {limit} passages.')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Level')
    #ax.set_xlim(-10, 10)
    #ax.set_ylim(0, 20)
    ax.set_zlim(-20, 10)
    ax.legend()
    plt.show()
