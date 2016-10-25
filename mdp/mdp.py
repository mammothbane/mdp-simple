import json
from itertools import count

from .coord import Coord


class MDP:
    def __init__(self, filename, reward=None, gamma=None):
        with open(filename) as f:
            data = json.load(f)

        self.gamma = gamma if gamma else data['gamma']
        self.dimens = Coord(data['dimens']['x'], data['dimens']['y'])
        self.reward = reward if reward else data['reward']
        assert reward

        self._squares = [_Col(self.dimens.y, x + 1, self) for x in range(self.dimens.x)]

        goals = data['goal']
        water = data['water']
        empty = data['empty']

        water_squares = []
        for i in range(water['x1'], water['x2']+1):
            for j in range(water['y1'], water['y2']+1):
                water_squares.append(Coord(i, j))

        for square in self:
            square.reward = self.reward

            for g in goals:
                if g['x'] == square.x and g['y'] == square.y:
                    square.final = True
                    square.reward = g['score']
                    square.utility = [g['score']]

            for w in water_squares:
                if w.x == square.x and w.y == square.y:
                    square.water = True
                    square.water_dir = water['dir']
                    square.chance = water['chance']

            for e in empty:
                if e['x'] == square.x and e['y'] == square.y:
                    square.empty = True

    def __getitem__(self, item):
        if item == 0:
            raise IndexError

        return self._squares[item - 1]

    def __iter__(self):
        """Yield all squares in the problem."""
        for col in self._squares:
            yield from col

    def _print(self, utility=False, reward=False, policy=False):
        s = ''
        for j in range(self.dimens.y):
            for i in range(self.dimens.x):
                sq = self[i + 1][j + 1]

                sqval = 0
                if utility:
                    sqval = sq.utility[-1]
                elif reward:
                    sqval = sq.reward

                sqval = '%.3f' % sqval

                delim = ' '

                if sq.empty:
                    sqval = 'x'
                elif sq.chance != 0:
                    delim = '~'
                elif sq.final:
                    delim = '|'

                s += ('%s%s%s' % (delim, sqval, delim)).rjust(10)
            s += '\n'
        print(s)

    def print_utility(self):
        self._print(utility=True)

    def print_reward(self):
        self._print(reward=True)

    def print_policy(self):
        self._print(policy=True)

    def value_iterate(self):
        for i in count(1):
            delta_ok = True

            for sq in self:
                if sq.empty:
                    continue
                try:
                    if sq.water_dir == 'l':
                        water_tgt = sq.left
                    elif sq.water_dir == 'r':
                        water_tgt = sq.right
                    elif sq.water_dir == 'd':
                        water_tgt = sq.down
                    elif sq.water_dir == 'u':
                        water_tgt = sq.up
                except IndexError:
                    assert sq.chance == 0
                    water_tgt = sq

                if water_tgt.empty:
                    water_tgt = sq

                if sq.final:
                    new_util = sq.reward
                else:
                    new_util = sq.reward + self.gamma * (max([elem.utility[i - 1]*(1 - sq.chance) +
                                                              water_tgt.utility[i - 1] * sq.chance
                                                              for elem in sq.adjacent()]))

                sq.utility.append(new_util)
                if i < 3 or abs(sq.utility[-1] - sq.utility[-2]) > 0.0001:
                    delta_ok = False

            if delta_ok:
                break


class _Col:
    def __init__(self, size, x, parent):
        self.x = x
        self.squares = [_Square(Coord(x, y + 1), parent) for y in range(size)]

    def __getitem__(self, item):
        if item == 0:
            raise IndexError

        return self.squares[item - 1]

    def __iter__(self):
        yield from self.squares


class _Square:
    def __init__(self, coord, parent, reward=0, utility=0, final=False):
        self.parent = parent
        self.coord = coord
        self.reward = reward
        self.final = final
        self.utility = [utility]

        self.empty = False

        self.water_dir = 'l'
        self.chance = 0

    @property
    def x(self):
        return self.coord.x

    @property
    def y(self):
        return self.coord.y

    @property
    def left(self):
        return self.parent[self.coord.x - 1][self.coord.y]

    @property
    def right(self):
        return self.parent[self.coord.x + 1][self.coord.y]

    @property
    def up(self):
        return self.parent[self.coord.x][self.coord.y - 1]

    @property
    def down(self):
        return self.parent[self.coord.x][self.coord.y + 1]

    def adjacent(self):
        if self.coord.x > 1:
            if not self.left.empty:
                yield self.left

        if self.coord.y > 1:
            if not self.up.empty:
                yield self.up

        if self.coord.y < self.parent.dimens.y:
            if not self.down.empty:
                yield self.down

        if self.coord.x < self.parent.dimens.x:
            if not self.right.empty:
                yield self.right

    def __repr__(self):
        return '(%s, %s): R: %s, U: %s%s' % \
               (self.x, self.y, self.reward, self.utility[-1], ', final' if self.final else '')
