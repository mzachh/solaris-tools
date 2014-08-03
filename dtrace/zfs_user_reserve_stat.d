#!/usr/sbin/dtrace -s
/*
 * zfs_user_reserve_stat.d
 *
 * Shows statistics of ZFS ARC and the user_reserve_hint_pct kernel parameter.
 *
 *
 * Details: http://blog.zach.st/2014/08/02/control-the-size-of-the-zfs-arc-cache-dynamically.html
 *
 * Usage: ./zfs_user_reserve_stat.d <interval in sec>
 *        ./zfs_user_reserve_stat.d 10
 *
 *
 * Copyright (c) 2014 Manuel Zach, All rights reserved.
*/

#pragma D option quiet

dtrace:::BEGIN
{
        pagesize = `_pagesize;
        mb = 1024*1024;
        printf("    PHYS      ARC  USR avail (MB)  USR(%%)  user_reserve_hint_pct (MB)  user_reserve_hint_pct (%%)\n");
}

profile:::tick-$1sec
{
        physmem = (`physmem * pagesize) / mb;
        user_reserved_pct = `user_reserve_hint_pct;
        user_reserved = (user_reserved_pct * physmem) / 100;
        arc_size = `arc_stats.arcstat_size.value.ui64 / mb;
        used_by_kernel = (`kpages_locked * pagesize) / mb;
        current_mem_userspace_pct = ((physmem - used_by_kernel) * 100) / physmem;
        current_mem_userspace = physmem - used_by_kernel;

        printf("%8d %8d %15d %7d %27d %26d\n", physmem, arc_size, current_mem_userspace,
                current_mem_userspace_pct,user_reserved,user_reserved_pct);
}
