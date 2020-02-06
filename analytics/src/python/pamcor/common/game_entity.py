#
# Copyright (C) Stanislaw Adaszewski, 2018
#

class Entity(object):
    def __init__(self, x, y, delay, dx=0, dy=0):
        self.x, self.y, self.delay, self.dx, self.dy = \
            x, y, delay, dx, dy
        self.t = 0

    def move(self, t, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.t = t

    def sample_pos(self, t):
        delta = t - self.t
        delay = self.delay

        if delta > delay:
            x = self.x + self.dx
            y = self.y + self.dy
        else:
            x = self.x + self.dx * delta / delay
            y = self.y + self.dy * delta / delay

        return (x, y)
