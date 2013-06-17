#!/usr/bin/python
# Version: 17th May 2013

# Monitor: vmstat 3 | python f_vmstat.py 


import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = False


hostname = platform.node()

lines=[]
ignore_lines=1

if not DEBUG_LOCAL:
    sock = socket()
    try:
        sock.connect( (CARBON_SERVER,CARBON_PORT) )
    except:
        print "Couldn't connect to %(server)s on port %(port)d, is carbon-agent.py running?" % { 'server':CARBON_SERVER, 'port':CARBON_PORT }
        sys.exit(1)


while 1:
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        break
    if not line:
        break
    if 'swap' in line:
        continue
    if 'memory' in line:
        continue

    parts = line.split()
    if len(parts)==0:
        continue

    if ignore_lines>0:
        ignore_lines-=1
        continue

    now=int(time.time())
    scan_rate = parts[11]
    lines.append("DEMO.%s.memory.scanrate %s %d" % (hostname,scan_rate,now))


    message = '\n'.join(lines) + '\n'

    if DEBUG_LOCAL:
        print [message]
        sys.stdout.flush()
    else:
        sock.sendall(message)

    lines = []

if not DEBUG_LOCAL:
    sock.close()

