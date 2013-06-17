#!/usr/bin/dtrace
#pragma D option quiet

dtrace:::BEGIN
{
    new_procs = 0;
}

proc:::exec-success
{
    new_procs++;
} 

tick-10sec
{
    printf("DEMO.sol11demo1.dtrace.new_procs %d %d\n", new_procs, walltimestamp / 1000000000);
    new_procs = 0;
}
