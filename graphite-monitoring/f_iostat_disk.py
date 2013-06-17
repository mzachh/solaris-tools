#!/usr/bin/python
# Version: 5th Nov 2012

# Monitor: iostat -xrCMT u 30 10000


import time
import sys
import platform
from socket import socket

CARBON_SERVER = "127.0.0.1"
CARBON_PORT = 2003
DEBUG_LOCAL = False

hostname = platform.node()
now=0
sum_reads=0
sum_readMB=0
sum_writes=0
sum_writeMB=0

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

    parts = line.split(",")
    if len(parts)==0:
        continue

    if parts[0].strip().isdigit():
        now = str(parts[0].strip())
        
        # Hint: summary is only printed in the next cycle
        if (sum_reads+sum_writes+sum_readMB+sum_writeMB)!=0:
            lines.append("DEMO."+hostname+".io.sum.reads.IO_s "+str(sum_reads)+" "+str(now))
            lines.append("DEMO."+hostname+".io.sum.writes.IO_s "+str(sum_writes)+" "+str(now))
            lines.append("DEMO."+hostname+".io.sum.reads.MB_s "+str(sum_readMB)+" "+str(now))
            lines.append("DEMO."+hostname+".io.sum.writes.MB_s "+str(sum_writeMB)+" "+str(now))
            sum_reads=0
            sum_readMB=0
            sum_writes=0
            sum_writeMB=0

    if parts[0][0]=="c":
        sum_reads += float(parts[1])
        sum_readMB += float(parts[3])
        sum_writes += float(parts[2])
        sum_writeMB += float(parts[4])
        lines.append("DEMO."+hostname+".io."+str(parts[0])+".reads.IO_s "+str(parts[1])+" "+str(now))
        lines.append("DEMO."+hostname+".io."+str(parts[0])+".writes.IO_s "+str(parts[2])+" "+str(now))
        lines.append("DEMO."+hostname+".io."+str(parts[0])+".reads.MB_s "+str(parts[3])+" "+str(now))
        lines.append("DEMO."+hostname+".io."+str(parts[0])+".writes.MB_s "+str(parts[4])+" "+str(now))

    message = '\n'.join(lines)
    if message:
        message += '\n'

    if DEBUG_LOCAL:
	print [message]
	sys.stdout.flush()
    else:
	sock.sendall(message)

    lines=[]

if not DEBUG_LOCAL:
    sock.close()



close()

