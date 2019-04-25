import sys
from subprocess import Popen, PIPE

import requests
from prettytable import PrettyTable


def main():
    address = sys.argv[0]
    adrs = input()

    table = PrettyTable(["Number", "IP", "AS", "CITY", "COUNTRY"])
    p = Popen(['tracert', "-d", adrs], stdout=PIPE)
    AS, city, ip, country, counter = '', '', '', '', 0
    while True:
        line = p.stdout.readline().decode('cp1256')
        if 'ms' in line:
            ip = line.split(' ')[-2]
            data = requests.get('https://ipinfo.io/{}/json'.format(ip))
            data_lines = data.text.split('\n')
            for data in data_lines:
                if 'org' in data:
                    AS = data.split(':')[-1]
                elif 'city' in data:
                    city = data.split(':')[-1]
                elif 'country' in data:
                    country = data.split(':')[-1]

            counter += 1
            table.add_row([counter, ip, AS, city, country])
            print(table)

        if not line:
            break


if __name__ == "__main__":
    main()