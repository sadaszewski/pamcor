class SlidingTimeWindow(object):
    def __init__(self, width):
        self.width = width
        self.samples = []

    def append(self, t, value):
        if len(self.samples) > 0 and t - self.samples[0][0] > 2 * self.width:
            self.samples = list(filter(lambda a: a[0] <= self.width, self.samples))
        self.samples.append((t, value))

    def look_in_the_past(self, t):
        for i in range(len(self.samples) - 1, -1, -1):
            # print(self.samples[i][0])
            if self.samples[i][0] <= t:
                return self.samples[i][1]
