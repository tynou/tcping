#!/usr/bin/env python3
import socket
import argparse
import sys
from ping import Ping


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]


def get_free_port():
    for port in range(49152, 65535):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", port))
                return port
            except socket.error:
                continue
    return None


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("host", type=str)
    parser.add_argument("-p", "--port", type=int, required=False, default=80)
    parser.add_argument("-c", "--count", type=int, required=False, default=float('Inf'))
    parser.add_argument("-t", "--timeout", type=float, required=False, default=5.0)
    parser.add_argument("-i", "--interval", type=float, required=False, default=1.0)
    parser.add_argument("-d", "--debug", required=False, default=False, action="store_true")

    args = parser.parse_args()

    return args


if __name__ == "__main__":
    args = parse_args()

    try:
        socket.inet_aton(args.host)
        dst_ip = args.host
    except socket.error:
        try:
            dst_ip = socket.gethostbyname(args.host)
        except socket.error:
            print(f"Хоста '{args.host}' не существует")
            sys.exit(1)
    
    if dst_ip == "127.0.0.1":
        src_ip = "127.0.0.1"
    else:
        src_ip = get_local_ip()
    
    src_port = get_free_port()

    ping = Ping(src_ip, src_port, dst_ip, args.port, args.timeout, args.debug)
    try:
        ping.start(args.count, args.interval)
    except KeyboardInterrupt:
        ping.print_statistics()
