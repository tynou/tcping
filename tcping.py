#!/usr/bin/env python3
import socket
import argparse
from ping import Ping


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]


def get_free_port():
    for port in range(49152, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except socket.error:
                continue
    return None


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', type=str, help='host to ping')
    parser.add_argument('-p', '--port', dest='port', type=int, required=False, default=80)
    parser.add_argument('-c', '--count', dest='count', type=int, required=False, default=float('Inf'))
    parser.add_argument('-t', '--timeout', dest='timeout', type=int, required=False, default=5)
    parser.add_argument('-i', '--interval', type=float, required=False, default=1)
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = parse_args()

    dst_ip = socket.gethostbyname(args.host)
    src_ip = get_ip()
    src_port = get_free_port()

    ping = Ping(src_ip, src_port, dst_ip, args.port, args.timeout)
    try:
        ping.start(args.count, args.interval)
    except KeyboardInterrupt:
        ping.print_statistics()
