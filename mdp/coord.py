class Coord:
    def __init__(self, x, y):
        self._data = (x, y)

    @property
    def x(self):
        return self._data[0]

    @property
    def y(self):
        return self._data[1]

    def __str__(self):
        return 'Coord(%s, %s)' % (self.x, self.y)

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)