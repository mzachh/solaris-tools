#!/usr/bin/python
# Version: 12th May 2013

# Monitor: kstat -p unix:0:kmem_slab_cache:slab_size unix:0:system_pages:physmem unix:0:system_pages:freemem zfs:0:arcstats:size unix:0:system_pages:lotsfree 30 1000 | python f_kstat_memory.py


import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = False


hostname = platform.node()

physmem=0
freemem=0
arc_size=0
pagesize=0

lines=[]

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

    if "used" in line:
        continue
    parts = line.split()
    if len(parts)==0:
        continue

    now=int(time.time())
    if "physmem" in line:
        physmem = int(parts[1])
        lines.append("DEMO."+hostname+".memory.physmem "+str((physmem*pagesize))+" "+str(now))
    if "freemem" in line:
        freemem = int(parts[1])
        lines.append("DEMO."+hostname+".memory.freemem "+str((freemem*pagesize))+" "+str(now))
    if "arcstats" in line:
        arc_size = int(parts[1])
        lines.append("DEMO."+hostname+".memory.arc_size "+str((arc_size))+" "+str(now))
        lines.append("DEMO."+hostname+".memory.used "+str( ( (physmem*pagesize) -((freemem*pagesize)+(arc_size)) ) )+" "+str(now))
    if "slab_size" in line:
        pagesize = int(parts[1])
    if "lotsfree" in line:
        lotsfree = int(parts[1])
        lines.append("DEMO."+hostname+".memory.lotsfree "+str((lotsfree*pagesize))+" "+str(now))

    message = '\n'.join(lines)
    if message:
	message += '\n'

    if DEBUG_LOCAL:
	print [message]
	sys.stdout.flush()
    else:
	sock.sendall(message)

    lines = []
sock.close()

