from response import Response


def avg(*nums):
    return sum(nums) / len(nums)


class Stats:
    def __init__(self):
        self.records = []
        self.received = 0
        self.lost = 0

    def add(self, code, time):
        if time != 0:
            self.records.append(round(time * 1000, 3))

        if code == Response.PORT_OPEN:
            self.received += 1
        else:
            self.lost += 1

    def results(self):
        packet_stats = (
            f"\nСтатистика пакетов:\n"
            f"{self.lost + self.received} пакетов отправлено\n"
            f"{self.received} пакетов доставлено\n"
            f"Процент потерь - {self.lost / (self.lost + self.received) * 100:.1f}%\n"
        )

        time_stats = ""
        if len(self.records) != 0:
            time_stats = (
                f"Статистика времени:\n"
                f"min - {min(self.records):.1f}ms\n"
                f"max - {max(self.records):.1f}ms\n"
                f"avg - {avg(*self.records):.1f}ms"
            )

        return packet_stats + time_stats
