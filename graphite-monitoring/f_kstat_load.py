#!/usr/bin/python
# Version: 12th May 2013

# Monitor: kstat -p unix:0:system_misc:avenrun_* 60 | python f_kstat_load.py


import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = False


hostname = platform.node()

lines=[]

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

    parts = line.split()
    if len(parts)==0:
        continue

    now=int(time.time())

    # load value
    if "avenrun_" in line:
        attr_name=parts[0].split(":")[-1]
        load = int(parts[1])
        lines.append("DEMO.%s.system.%s %.2f %d" % (hostname,attr_name,load/256.0,now))


    message = '\n'.join(lines) + '\n'

    if DEBUG_LOCAL:
        print message
        sys.stdout.flush()
    else:
        sock.sendall(message)

    lines = []

if not DEBUG_LOCAL:
    sock.close()

