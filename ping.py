import time
import itertools
import struct
import socket
from response import Response
from stats import Stats


def get_checksum(data):
    checksum = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        checksum += (data[i]) + ((data[i + 1]) << 8)
        if n:
            checksum += (data[i + 1])
    while checksum >> 16:
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    checksum = ~checksum & 0xffff
    return checksum


class Ping:
    def __init__(self, src_ip, src_port, dst_ip, dst_port, timeout):
        self.tcp = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

        self.src_ip = src_ip
        self.src_port = src_port
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.timeout = timeout
        self.stats = Stats()
    
    def print_statistics(self):
        print(self.stats.results())

    def start(self, count, interval):
        counter = itertools.count(1)
        while count:
            code, response_time = self.ping(next(counter))
            self.stats.add(code, response_time)
            # print(f"Ping {self.dst_ip}:{self.dst_port} | {code} | time={round(response_time * 1000, 3)}ms")
            match code:
                case Response.PORT_OPEN:
                    print(f"{self.dst_ip}:{self.dst_port} | Порт отрыт | Ответ получен за {round(response_time * 1000, 3)}мс")
                case Response.PORT_CLOSED:
                    print(f"{self.dst_ip}:{self.dst_port} | Порт закрыт")
                case Response.TIMEOUT:
                    print(f"{self.dst_ip}:{self.dst_port} | Нет ответа | Время истекло")
            count -= 1
            if interval - response_time > 0:
                time.sleep(interval - response_time)
        
        self.print_statistics()

    def ping(self, seq):
        self.tcp.settimeout(self.timeout)
        tcp_packet = self.build(seq, 2)

        try:
            self.tcp.sendto(tcp_packet, (self.dst_ip, self.dst_port))
            start_time = time.time()

            while True:
                response = self.tcp.recvfrom(16384)  # Чтение ответа
                if not response:
                    continue
                data, _ = response
                response_time = time.time() - start_time

                # Разбор TCP-заголовка
                tcp_header = struct.unpack('!BBBBIIBB', data[20:34])
                ack_seq = tcp_header[5]  # Номер подтверждения (ACK)
                flags = tcp_header[7]    # Флаги TCP

                if ack_seq == seq + 1:  # Проверка ACK
                    if flags == 0x12:    # SYN-ACK (порт открыт)
                        self.tcp.sendto(self.build(seq, 4), (self.dst_ip, self.dst_port))  # RST (закрытие)
                        return Response.PORT_OPEN, response_time
                    elif flags == 0x04 or flags == 0x14:   # RST (порт закрыт) или RST и ACK
                        return Response.PORT_CLOSED, response_time
        except socket.timeout:
            return Response.TIMEOUT, 0

    def build(self, seq, flags):
        packet = struct.pack(
            '!HHIIBBHHH',
            self.src_port,  # Source Port
            self.dst_port,  # Destination Port
            seq,              # SEQ
            0,              # ACK
            5 << 4,         # Data Offset
            flags,     # Flags
            1024,           # Window
            0,              # Checksum
            0               # Urgent pointer
        )

        header = struct.pack(
            '!4s4sHH',
            socket.inet_aton(self.src_ip),
            socket.inet_aton(self.dst_ip),
            socket.IPPROTO_TCP,
            len(packet)
        )

        checksum = get_checksum(header + packet)
        packet = packet[:16] + struct.pack('H', checksum) + packet[18:]

        return packet
