#!/usr/bin/dtrace
#pragma D option quiet

dtrace:::BEGIN
{
    tcp_accepts = 0;
}

fbt:ip:tcp_accept:entry
{
    tcp_accepts++;
} 

tick-10sec
{
    printf("DEMO.sol11demo1.dtrace.tcp_accept %d %d\n", tcp_accepts, walltimestamp / 1000000000);
    tcp_accepts = 0;
}
