from response import Response


def avg(*nums):
    return sum(nums) / len(nums)


class Stats:
    def __init__(self):
        self.records = []
        self.received = 0
        self.lost = 0
        # packets sent
        # packets delivered
        # packet loss %
        # min, max, avg response times

    def add(self, code, time):
        if time != 0:
            self.records.append(round(time * 1000, 3))

        if code == Response.PORT_OPEN:
            self.received += 1
        else:
            self.lost += 1

    def results(self):
        return f"{self.lost / (self.lost + self.received) * 100:.1f}% lost\nmin - {min(self.records)}ms\nmax - {max(self.records)}ms\navg - {avg(*self.records)}ms"
    