import json
from itertools import count

from .coord import Coord


class MDP:
    """The representation of the whole problem."""
    def __init__(self, filename, reward=None, gamma=None, precision=None):
        with open(filename) as f:
            data = json.load(f)

        self.dimens = Coord(data['dimens']['x'], data['dimens']['y'])

        self.gamma = gamma if gamma else data['gamma']
        self.precision = precision if precision else data['precision']
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

                sqval = '%.2f' % sqval

                delim = ' '

                if sq.empty:
                    sqval = 'x'
                elif sq.chance != 0:
                    delim = '~'
                elif sq.final:
                    delim = '|'

                if policy:
                    sqval = sq.policy()
                    if not sqval:
                        sqval = ' '
                    delim = ' '
                    if sq.empty:
                        sqval = 'x'
                    if sq.final:
                        sqval = 'F'

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
        """Run the value iteration algorithm until within the specified precision."""
        for i in count(1):
            delta_ok = True

            for sq in self:
                if sq.empty:
                    continue

                if sq.final:
                    new_util = sq.reward
                else:
                    new_util = sq.reward + self.gamma * (max([elem.utility[i - 1]*(1 - sq.chance) +
                                                              sq.water_target.utility[i - 1] * sq.chance
                                                              for elem in sq.adjacent()]))

                sq.utility.append(new_util)
                if i < 5 or abs(sq.utility[-1] - sq.utility[-2]) > self.precision:
                    delta_ok = False

            if delta_ok:
                break


class _Col:
    """
    A column of tiles.

    Utility class so that we can address tiles by their [x][y] coordinates.
    """
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
        return [x for _, x in self.adjacent_dict()]

    def adjacent_dict(self):
        if self.coord.x > 1:
            if not self.left.empty:
                yield '<', self.left

        if self.coord.y > 1:
            if not self.up.empty:
                yield '^', self.up

        if self.coord.y < self.parent.dimens.y:
            if not self.down.empty:
                yield 'v', self.down

        if self.coord.x < self.parent.dimens.x:
            if not self.right.empty:
                yield '>', self.right

    @property
    def water_target(self):
        try:
            if self.water_dir == 'l':
                elem = self.left
            elif self.water_dir == 'r':
                elem = self.right
            elif self.water_dir == 'd':
                elem = self.down
            elif self.water_dir == 'u':
                elem = self.up

            if elem.empty:
                return self

            return elem

        except IndexError:
            assert self.chance == 0
            return self

    def policy(self):
        if self.empty or self.final:
            return

        opts = {direction: self.water_target.utility[-1]*self.chance + elem.utility[-1]*(1 - self.chance) for direction, elem in
                self.adjacent_dict()}

        return max(opts, key=opts.get)

    def __repr__(self):
        return '(%s, %s): R: %s, U: %s%s' % \
               (self.x, self.y, self.reward, self.utility[-1], ', final' if self.final else '')
