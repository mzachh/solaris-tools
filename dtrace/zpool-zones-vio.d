#!/usr/sbin/dtrace -s
/*
 * zpool-zones-vio.d  
 *
 * ZFS statistics per zpool and per zone.
 *
 * The scipt sums up all write and read I/O per zpool and per zone.
 *
 * Details: http://blog.zach.st/2013/10/zpool-zones-viod-zfs-statistics-per-zpool-and-per-zone.html
 * 
 * Usage: ./zpool-zones-vio.d <interval>
 *        ./zpool-zones-vio.d 10s
 *
 * Notes: I/O errors are not considered, therefore failed I/O is also counted.  
 *
 * Copyright (c) 2013 Manuel Zach, All rights reserved.
*/

#pragma D option quiet
#pragma D option dynvarsize=8m

fbt:zfs:zfs_read:entry,
fbt:zfs:zfs_write:entry
{
    self->in = 1;
    self->zpool_name = (string)((znode_t *)args[0]->v_data)->z_zfsvfs->z_os->os_spa->spa_name;
    self->iosize = args[1]->uio_resid;
}

fbt:zfs:zfs_read:return
/self->in/
{
    @zfs_reads_bytes[self->zpool_name,zonename] = sum(self->iosize);
    @zfs_reads[self->zpool_name,zonename] = count();
}

fbt:zfs:zfs_write:return
/self->in/
{
    @zfs_writes_bytes[self->zpool_name,zonename] = sum(self->iosize);
    @zfs_writes[self->zpool_name,zonename] = count();
}

fbt:zfs:zfs_read:return,
fbt:zfs:zfs_write:return
/self->in/
{
    self->in =0;
    self->zpool_name = 0;
    self->iosize = 0;
}


tick-$1
{
    normalize(@zfs_reads_bytes,1024);
    normalize(@zfs_writes_bytes,1024);
    printf("\n\n%20s\t%15s\t%5s\t%10s\t%5s\t%10s\n","zpool","zonename","reads","reads(KB)", "writes","writes(KB)");
    printf("%20s\t%15s\t%5s\t%10s\t%5s\t%10s\n","-----","--------","-----","---------", "------","----------");
    printa("%20s\t%15s\t%@5u\t%@10u\t%@5u\t%@10u\n",@zfs_reads,@zfs_reads_bytes,@zfs_writes,@zfs_writes_bytes);
    trunc(@zfs_reads);
    trunc(@zfs_reads_bytes);
    trunc(@zfs_writes);
    trunc(@zfs_writes_bytes);
}
