import flask
import json
import subprocess

def jsonify(data=None, status_code=None):
    if not isinstance(data, basestring):
        data = json.dumps(data)
    response = flask.Response(response=data, mimetype='application/json')
    response.headers.add('Cache-Control',
        'no-cache, no-store, must-revalidate')
    response.headers.add('Pragma', 'no-cache')
    if status_code is not None:
        response.status_code = status_code
    return response

def rmtree(path):
    subprocess.check_call(['rm', '-r', path])

def check_output(*popenargs, **kwargs):
    # For python2.6 support
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, ' + \
            'it will be overridden.')
    process = subprocess.Popen(stdout=subprocess.PIPE,
        *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get('args')
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output

def ip_to_long(ip_str):
    ip = ip_str.split('.')
    ip.reverse()
    while len(ip) < 4:
        ip.insert(1, '0')
    return sum(long(byte) << 8 * i for i, byte in enumerate(ip))

def long_to_ip(ip_num):
    return '.'.join(map(str, [
        (ip_num >> 24) & 0xff,
        (ip_num >> 16) & 0xff,
        (ip_num >> 8) & 0xff,
        ip_num & 0xff,
    ]))

def subnet_to_cidr(subnet):
    count = 0
    while ~ip_to_long(subnet) & pow(2, count):
        count += 1
    return 32 - count

def network_addr(ip, subnet):
    return '%s/%s' % (long_to_ip(ip_to_long(ip) & ip_to_long(subnet)),
        subnet_to_cidr(subnet))

def get_network_addr():
    addresses = []
    output = check_output(['ifconfig'])
    for interface in output.split('\n\n'):
        interface_name = re.findall(r'[a-z0-9]+', interface, re.IGNORECASE)
        if not interface_name:
            continue
        interface_name = interface_name[0]
        if re.search(r'tun[0-9]+', interface_name) or interface_name == 'lo':
            continue
        addr = re.findall(r'inet.{0,10}\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            interface, re.IGNORECASE)
        if not addr:
            continue
        addr = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            addr[0], re.IGNORECASE)
        if not addr:
            continue
        mask = re.findall(r'mask.{0,10}\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            interface, re.IGNORECASE)
        if not mask:
            continue
        mask = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            mask[0], re.IGNORECASE)
        if not mask:
            continue
        addr = addr[0]
        mask = mask[0]
        if addr.split('.')[0] == '127':
            continue
        addresses.append(network_addr(addr, mask))
    return addresses
