#!/usr/bin/env python3
import socket
import argparse
import sys
from ping import Ping


def get_local_ip(v6):
    if v6:
        ip_prot = socket.AF_INET6
        dns_ip = "2001:4860:4860::8888"
    else:
        ip_prot = socket.AF_INET
        dns_ip = "8.8.8.8"
    s = socket.socket(ip_prot, socket.SOCK_DGRAM)
    s.connect((dns_ip, 80))
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

    parser.add_argument("host", type=str, nargs="+")
    parser.add_argument("-p", "--port", type=int, required=False, default=[80], nargs="+")
    parser.add_argument("-c", "--count", type=int, required=False, default=float("Inf"))
    parser.add_argument("-t", "--timeout", type=float, required=False, default=5.0)
    parser.add_argument("-i", "--interval", type=float, required=False, default=1.0)
    parser.add_argument("-d", "--debug", required=False, default=False, action="store_true")
    parser.add_argument("-6", "--ipv6", action="store_true")

    args = parser.parse_args()

    return args


def resolve_host(host, v6):
    if v6:
        if is_valid_ipv6(host):
            return host
        else:
            ipv6 = get_ipv6_address(host)
            if len(ipv6) > 0:
                return ipv6[0]
            else:
                print("Не найдено ни одного IPv6 адреса для этого хоста.")
                return None
    else:
        try:
            socket.inet_aton(host)
            return host
        except socket.error:
            try:
                return socket.gethostbyname(host)
            except socket.error:
                print(f"Хоста '{host}' не существует")
                return None


def get_ipv6_address(host):
    try:
        addr_info = socket.getaddrinfo(host, None, socket.AF_INET6)
        ipv6_addresses = [info[4][0] for info in addr_info]
        return ipv6_addresses
    except socket.error:
        print("Данный компьютер не имеет IPv6 адреса")
        sys.exit(1)


def is_valid_ipv6(ip):
    try:
        socket.inet_pton(socket.AF_INET6, ip)
        return True
    except socket.error:
        return False


if __name__ == "__main__":
    args = parse_args()

    hosts = args.host

    resolved_ips = []
    for host in hosts:
        ip = resolve_host(host, args.ipv6)
        if ip is not None:
            resolved_ips.append(ip)

    if not resolved_ips:
        print("Не указано ни одного валидного хоста")
        sys.exit(1)

    ports = args.port

    src_ip = "127.0.0.1" if "127.0.0.1" in resolved_ips else get_local_ip(args.ipv6)
    src_port = get_free_port()

    for i, dst_ip in enumerate(resolved_ips):
        port = ports[0] if i >= len(ports) else ports[i]
        print(f"Начинаю отправку TCP пакетов на {dst_ip}:{port} от {src_ip}:{src_port}")
        ping = Ping(src_ip, src_port, dst_ip, port, args.timeout, args.debug, args.ipv6)
        try:
            ping.start(args.count, args.interval)
        except KeyboardInterrupt:
            ping.print_statistics()
