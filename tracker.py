import sys
import requests
import re
import platform

from subprocess import Popen, PIPE, check_output, DEVNULL
from prettytable import PrettyTable


POLLED_SERVICES = ['https://ipinfo.io/{}/json', 'http://ip-api.com/json/{}']


def service_request(service: str, address: str) -> dict:
    url = service.format(address)
    data = requests.get(url)
    data = data.json()
    keys = ("org", "city", "country")
    return {key: data[key] if key in data.keys() else '?' for key in keys}


def request_ip_data(address: str) -> dict:
    for service in POLLED_SERVICES:
        try:
            data = service_request(service, address)
        except requests.RequestException:
            continue
        else:
            break
    else:
        return {}
    return data


def trace_win(address: str) -> tuple:
    popen = Popen(('tracert', "-d", address), stdout=PIPE)
    ip_addresses = list()
    while True:
        line = popen.stdout.readline().decode('cp1256')
        if 'ms' in line:
            ip_addresses.append(line.split(' ')[-2])
        if not line:
            break
    return tuple(ip_addresses)


def trace_linux(address: str, max_hops=30) -> tuple:
    result = str(check_output("sudo traceroute -I -m {} {}".format(max_hops, address), shell=True, stderr=DEVNULL))
    ip_pattern = re.compile('\([0-9]+(?:\.[0-9]+){3}\)')
    ip_addresses = list()
    for line in result.split('\\n'):
        ip = re.findall(ip_pattern, line)
        ip = ip[0][1:-1] if ip else ''
        ip_addresses.append(ip)
    return tuple(ip_addresses[1:-1])


def main():
    address = sys.argv[1]
    system = platform.system()
    if system == 'Windows':
        route = trace_win(address)
    elif system in ['Linux', 'Darwin']:
        route = trace_linux(address)
    else:
        print("Unknown OS")
        return

    table = PrettyTable(("Number", "IP", "AS", "CITY", "COUNTRY"))
    for counter, ip in enumerate(route):
        if ip:
            data = request_ip_data(ip)
            table.add_row((counter + 1, ip, data['org'], data['city'], data['country']))
        else:
            table.add_row((counter + 1, '*', '*', '*', '*'))
    print(table)


if __name__ == "__main__":
    main()
