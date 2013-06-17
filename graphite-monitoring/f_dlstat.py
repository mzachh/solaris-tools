#!/usr/bin/python
# Version: 17th May 2013

# Monitor: dlstat -p -o link,ipkts,rbytes,opkts,obytes -i 10 | python f_dlstat.py


import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = False


hostname = platform.node()

lines=[]
ignore_lines=4

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
    if '/' in line:
        continue

    parts = line.split(':')
    if len(parts)==0:
        continue

    if ignore_lines>0:
        ignore_lines-=1
        continue

    now=int(time.time())

    lines.append("DEMO.%s.network.%s.ipkgs %d %d" % (hostname,parts[0],int(parts[1]),now))
    lines.append("DEMO.%s.network.%s.rbytes %d %d" % (hostname,parts[0],int(parts[2]),now))
    lines.append("DEMO.%s.network.%s.opkgs %d %d" % (hostname,parts[0],int(parts[3]),now))
    lines.append("DEMO.%s.network.%s.obytes %d %d" % (hostname,parts[0],int(parts[4]),now))


    message = '\n'.join(lines) + '\n'

    if DEBUG_LOCAL:
        print [message]
        sys.stdout.flush()
    else:
        sock.sendall(message)

    lines = []

if not DEBUG_LOCAL:
    sock.close()

