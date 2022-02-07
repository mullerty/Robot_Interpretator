import sys

from Robot_Interpretator.Variables.Variables import Variable
import os
import time

directions = {
    0: 'RIGHT',
    1: 'DOWN',
    2: 'LEFT',
    3: 'UP'
}

cell_types = {
        ' ': 'EMPTY',
        '#': 'WALL',
        'O': 'EXIT'
    }


class Cell:
    def __init__(self, sign):
        self.type = cell_types[sign]
        self.sign = sign

    def __repr__(self):
        return f'{self.type}: \'{self.sign}\''


class Robot:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.map = None
        self.direction = 3
        self.fin = False

    def __repr__(self):
        return f'x = {self.x}, y = {self.y}; Direction: {directions[self.direction]}\n'

    def create_map(self, filename):
        with open(filename) as file:
            txt = file.read()
        txt = txt.split('\n')
        position = txt.pop(0).split(' ')
        map_size = txt.pop(0).split(' ')
        x_max = int(map_size[0])
        y_max = int(map_size[1])
        x_ex, y_ex = -1, -1
        self.x = int(position[0])
        self.y = int(position[1])
        self.map = [[0] * x_max for i in range(y_max)]
        for i in range(y_max):
            line = list(txt.pop(0))
            for j, sign in enumerate(line):
                self.map[i][j] = Cell(sign)
                if sign == 'O':
                    x_ex = j
                    y_ex = i
        if x_ex != -1 and y_ex != -1:
            return x_ex, y_ex
        else:
            sys.stderr.write("Error: Labyrinth has no exit!")
            raise Exception

    def print_map(self):
        print(self)
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                if i == self.y and j == self.x:
                    if self.direction == 0:
                        print('→', end='')
                    elif self.direction == 1:
                        print('↓', end='')
                    elif self.direction == 2:
                        print('←', end='')
                    else:
                        print('↑', end='')
                else:
                    print(self.map[i][j].sign, end='')
            print()
        print()

    def step(self):
        if self.direction == 0:   #Right
            if (self.map[self.y][self.x+1].type != 'WALL'):
                self.x = self.x + 1
                time.sleep(0.3)
                print("\n" * 80)
                self.print_map()
                return Variable('boolean', True)
        elif self.direction == 1: #DOWN
            if (self.map[self.y+1][self.x].type != 'WALL'):
                self.y = self.y + 1
                time.sleep(0.3)
                print("\n" * 80)
                self.print_map()
                return Variable('boolean', True)
        elif self.direction == 2: #LEFT
            if (self.map[self.y][self.x-1].type != 'WALL'):
                self.x = self.x - 1
                time.sleep(0.3)
                print("\n" * 80)
                self.print_map()
                return Variable('boolean', True)
        else:                     #UP
            if (self.map[self.y-1][self.x].type != 'WALL'):
                self.y = self.y - 1
                time.sleep(0.2)
                print("\n" * 80)
                self.print_map()
                return Variable('boolean', True)
        return Variable('boolean', False)

    def look(self):
        distance = 0
        x = self.x
        y = self.y
        if self.map[y][x].type == 'EMPTY':
            if self.direction == 0:   #Right
                x = x + 1
                while self.map[y][x].type == 'EMPTY':
                    distance = distance + 1
                    x = x + 1
            elif self.direction == 1: #DOWN
                y = y + 1
                while self.map[y][x].type == 'EMPTY':
                    distance = distance + 1
                    y = y + 1

            elif self.direction == 2: #LEFT
                x = x - 1
                while self.map[y][x].type == 'EMPTY':
                    distance = distance + 1
                    x = x - 1

            else:                     #UP
                y = y - 1
                while self.map[y][x].type == 'EMPTY':
                    distance = distance + 1
                    y = y - 1

        if self.map[y][x].type == 'EXIT':
            if distance != 0:
                print(-distance)
                return Variable('int', -distance)
            else:
                self.fin = True
                print(-999)
                return Variable('int', -999)
        else:
            print(distance)
            return Variable('int', distance)

    def back(self):
        self.direction = (self.direction + 2) % 4
        time.sleep(0.2)
        print("\n" * 80)
        self.print_map()

    def right(self):
        self.direction = (self.direction + 1) % 4
        time.sleep(0.2)
        print("\n" * 80)
        self.print_map()

    def left(self):
        self.direction = (self.direction + 3) % 4
        time.sleep(0.2)
        print("\n" * 80)
        self.print_map()

    def escaped(self, x_ex, y_ex):
        if self.x == x_ex and self.y == y_ex:
            return True
        return False


if __name__ == '__main__':
    robot = Robot()
    robot.create_map('Maps/Map3.txt')
    robot.print_map()
    robot.right()
    robot.print_map()
    #time.sleep(500)
    #robot.left()
    #robot.print_map()
    robot.left()
    robot.print_map()
    robot.back()
    robot.print_map()
    robot.step()
    robot.print_map()
    #robot.step('BACK')
    #robot.print_map()
    print(robot.look())