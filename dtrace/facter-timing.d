#!/usr/sbin/dtrace -s
/*
 * facter-timing.d 
 *
 * The script measures the execution time of commands called by Puppet's facter.
 *
 * Details: http://blog.zach.st/2014/07/27/troubleshoot-slow-puppet-facter-runs.html
 * 
 * Usage: ./facter-timing.d -c '/usr/local/bin/facter --timing'
 *
 * Copyright (c) 2014 Manuel Zach, All rights reserved.
*/

#pragma D option bufpolicy=fill
#pragma D option bufsize=1m
#pragma D option quiet

BEGIN
{
    printf("\n\n= Dtrace statistics =\n");
    printf("\nRuby facter PID: %d\n\n", $target);
    printf("PID\truntime (ms)\tcommand\n");
    printf("---\t------------\t-------\n");
}

proc:::exec-success
/ppid == $target/
{
    starttime[curpsinfo->pr_pid] = timestamp;
}

proc:::exit
/starttime[curpsinfo->pr_pid]/
{
    starttime[curpsinfo->pr_pid] = timestamp - starttime[curpsinfo->pr_pid];
    printf("%d\t%d\t\t%s\n", curpsinfo->pr_pid,starttime[curpsinfo->pr_pid] / 1000000,curpsinfo->pr_psargs);
}
