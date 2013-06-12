#!/usr/bin/python
# Version: 12th May 2013
# Monitor: zonestat -T u -p -P system,zones,total  3

import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = True  

hostname = platform.node()

lines = []

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
        line = line.replace('\n','')
    except KeyboardInterrupt:
        break
    if not line:
        break

    parts = line.split(':')
    if len(parts)==0:
        continue

    now=parts[0]
    zonestat_type=parts[3].replace('[','').replace(']','')
    zonestat_cpu_used=parts[4]
    zonestat_cpu_part=parts[5].replace('%','')
    zonestat_PhysMem_used=parts[8]
    # Normalize to MB
    if "K" in zonestat_PhysMem_used:
        zonestat_PhysMem_used = "%.2f" % (int(zonestat_PhysMem_used.replace('K','')) / 1024.0)
    if "M" in zonestat_PhysMem_used:
        zonestat_PhysMem_used = zonestat_PhysMem_used.replace('M','')
    if "G" in zonestat_PhysMem_used:
        zonestat_PhysMem_used = "%.2f" % (int(zonestat_PhysMem_used.replace('G','')) * 1024.0)
    zonestat_PhysMem_Pused=parts[9].replace('%','')

    zonestat_VirtMem_used=parts[11]
    # Normalize to MB
    if "K" in zonestat_VirtMem_used:
        zonestat_VirtMem_used = "%.2f" % (int(zonestat_VirtMem_used.replace('K','')) / 1024.0)
    if "M" in zonestat_VirtMem_used:
        zonestat_VirtMem_used = zonestat_VirtMem_used.replace('M','')
    if "G" in zonestat_VirtMem_used:
        zonestat_VirtMem_used = "%.2f" % (int(zonestat_VirtMem_used.replace('G','')) * 1024.0)
    zonestat_VirtMem_Pused=parts[12].replace('%','')

    if zonestat_type != 'system':
        zonestat_PhysNet_used=parts[14]
        # Normalize to MB
        if "K" in zonestat_PhysNet_used:
            zonestat_PhysNet_used = "%.2f" % (int(zonestat_PhysNet_used.replace('K','')) / 1024.0)
        elif "M" in zonestat_PhysNet_used:
            zonestat_PhysNet_used = zonestat_PhysNet_used.replace('M','')
        elif "G" in zonestat_PhysNet_used:
            zonestat_PhysNet_used = "%.2f" % (int(zonestat_PhysNet_used.replace('G','')) * 1024.0)
        else:
            zonestat_PhysNet_used = "%.2f" % (int(zonestat_PhysNet_used.replace('G','')) / 1024.0 / 1024.0)
        zonestat_PhysNet_Pused=parts[15].replace('%','')

    lines.append("DEMO.%s.zonestat.%s.cpu.used %s %s" % (hostname,zonestat_type,zonestat_cpu_used,now))
    lines.append("DEMO.%s.zonestat.%s.cpu.%%used %s %s" % (hostname,zonestat_type,zonestat_cpu_part,now))
    lines.append("DEMO.%s.zonestat.%s.PhysMem.used %s %s" % (hostname,zonestat_type,zonestat_PhysMem_used,now))
    lines.append("DEMO.%s.zonestat.%s.PhysMem.%%used %s %s" % (hostname,zonestat_type,zonestat_PhysMem_Pused,now))
    lines.append("DEMO.%s.zonestat.%s.VirtMem.used %s %s" % (hostname,zonestat_type,zonestat_VirtMem_used,now))
    lines.append("DEMO.%s.zonestat.%s.VirtMem.%%used %s %s" % (hostname,zonestat_type,zonestat_VirtMem_Pused,now))
    if zonestat_type != 'system':
        lines.append("DEMO.%s.zonestat.%s.PhysNet.used %s %s" % (hostname,zonestat_type,zonestat_PhysNet_used,now))
        lines.append("DEMO.%s.zonestat.%s.PhysNet.%%used %s %s" % (hostname,zonestat_type,zonestat_PhysNet_Pused,now))

    message = '\n'.join(lines)
    lines = []
    if message:
        message += '\n'

    if DEBUG_LOCAL:
        print message
        sys.stdout.flush()
    else:
        sock.sendall(message)

if not DEBUG_LOCAL:
    sock.close()
