#!/usr/bin/env python3
import subprocess
import ipaddress

headers = ['name', 'version', 'address']
ipv4 = ['ip', '-o', 'a']

result = subprocess.run(ipv4, capture_output=True)
stdout = result.stdout.decode('ascii')
for line in stdout.replace('  ', ' ').split('\n'):
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
        print(_)
