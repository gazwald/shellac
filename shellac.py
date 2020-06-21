#!/usr/bin/env python3
import subprocess
import ipaddress
import multiprocessing


pool_size = multiprocessing.cpu_count() * multiprocessing.cpu_count()

def get_subnets(ipv4_only: bool = True,
                skip_local: bool = True):
    headers = ['name', 'version', 'address']

    ip = ['ip', '-o', 'a']

    if ipv4_only:
        ip.insert(1, '-4')

    interfaces = list()
    result = subprocess.run(ip, capture_output=True)
    stdout = result.stdout.decode('ascii').replace('  ', ' ').split('\n')
    for line in stdout:
        if line:
            _ = line.split(' ')
            _ = _[1:5]
            _ = list(filter(None, _))
            _ = dict(zip(headers, _))
            _['subnet'] = ipaddress.ip_network(_['address'], False)
            _['address'], _['cidr'] = _['address'].split('/')
            if _['version'] == 'inet':
                _['address'] = ipaddress.IPv4Address(_['address'])
            elif _['version'] == 'inet6':
                _['address'] = ipaddress.IPv6Address(_['address'])

            if _['name'] == 'lo' and skip_local:
                pass
            else:
                interfaces.append(_)

    return interfaces

def ping(address: str):
    ping = ['ping', '-c1', '-q', address]
    result = subprocess.run(ping, capture_output=True)
    if result.returncode == 0:
        return {'address': address, 'up': True}
    else:
        return {'address': address, 'up': False}

def icmp_hunt(addresses: list):
    with multiprocessing.Pool(processes=pool_size) as p:
        return p.map(ping, addresses)


if __name__ == '__main__':
    subnets = get_subnets()
    for subnet in subnets:
        print(subnet)
        _ = [str(host) for host in subnet['subnet'].hosts()]
        result = icmp_hunt(_)
        for address in result:
            if address['up']:
                print(address)
