import sys
import requests
import re
import platform

from subprocess import Popen, PIPE, check_output, DEVNULL
from prettytable import PrettyTable


def ipinfo_request(address: str) -> dict:
    url = 'https://ipinfo.io/{}/json'.format(address)
    data = requests.get(url)
    data = data.json()
    keys = ("org", "city", "country")
    return {key: data[key] if key in data.keys() else '?' for key in keys}


def ip_api_request(address: str) -> dict:
    url = 'http://ip-api.com/json/{}'.format(address)
    data = requests.get(url)
    data = data.json()
    keys = ("org", "city", "country")
    return {key: data[key] if (key in data.keys() and data[key]) else '?' for key in keys}


def request_ip_data(address: str) -> dict:
    ip_apis = (ipinfo_request,
               ip_api_request)
    for api in ip_apis:
        try:
            data = api(address)
        except requests.RequestException:
            continue
        else:
            break
    else:
        return {}
    return data


def trace_win(address: str) -> tuple:
    p = Popen(('tracert', "-d", address), stdout=PIPE)
    ip = list()
    while True:
        line = p.stdout.readline().decode('cp1256')
        if 'ms' in line:
            ip.append(line.split(' ')[-2])
        if not line:
            break
    return tuple(ip)


def trace_linux(address: str) -> tuple:
    result = str(check_output("sudo traceroute -I {}".format(address), shell=True, stderr=DEVNULL)).split('\\n')
    ip = list()
    ip_pattern = re.compile('[0-9]+(?:\.[0-9]+){3}')
    for line in result[1:-1]:
        re_result = re.findall(ip_pattern, line)
        ip.append(re_result[0] if re_result else '')
    return tuple(ip)


def trace(address: str) -> tuple:
    system = platform.system()
    if system == 'Windows':
        return trace_win(address)
    elif system == 'Linux':
        return trace_linux(address)
    else:
        return ()


def main():
    address = sys.argv[1]
    route = trace(address)

    if not route:
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
