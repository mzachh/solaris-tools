#!/usr/sbin/dtrace -s

/*
 * oracle-pwrite-zfs-latency.d  
 *
 * Aka kernel_io_oulier.d for ZFS.
 *
 * Reports pwrite() syscalls of Oracle databases which stay too long in the ZIO
 * pipline. Mainly thought for analysing slow redolog writes on ZFS.
 * 
 * This script was inspired by the V$KERNEL_IO_OUTLIER view of Oracle 12c and
 * the kernel_io_oulier.d script.
 *
 * Details: http://blog.zach.st/2013/10/detect-slow-sync-writes-on-ZFS.html
 * 
 * Usage: ./oracle-pwrite-zfs-latency.d
 *        ./oracle-pwrite-zfs-latency.d | egrep "TIMESTAMP|---------|lgwr"
 *
 * ZIO_OUTLIER_THRESHOLD is configured for 100 000 000 ns (100ms)
 *
 * TOTAL_LATENCY:   Total time in microseconds the I/O spent in the kernel
 *                  TOTAL_LATENCY = ZIO_IN + ZIO_PIPELINE + ZIO_OUT
 * ZIO_IN:          Time in microseconds spent until I/O reaches ZIO pipeline
 * ZIO_PIPELINE:    Time in microseconds I/O spent in ZIO pipeline
 * ZIO_WAIT:        Time in microseconds spent for zio_wait() in ZIO pipeline,
 *                  most likely this time is used for waiting for physical I/O 
 *                  is completed
 * ZIO_OUT:         Time in microseconds spent after I/O has left ZIO pipeline
 *
 * Copyright (c) 2013 Manuel Zach, All rights reserved.
*/

#pragma D option quiet 
#pragma D option dynvarsize=8m
 
inline long ZIO_OUTLIER_THRESHOLD= 100000000;

syscall::pwrite:entry
/execname == "oracle" /
{
  self->in = 1;
  self->wts = walltimestamp;
  self->ts = timestamp;
  self->dev = fds[arg0].fi_name;

  self->iostartts = timestamp;

  self->ziostartts = 0;
  self->zioendts = 0;
  self->zio_wait = 0;
  self->zio_wait_startts = 0;
  self->zio_wait_endts = 0;
  self->pool_name = "";
}


/* Time write is processed in the ZIO pipline start */
fbt::zio_root:entry
/self->in && self->ziostartts == 0/
{
  self->ziostartts = timestamp;
}

fbt::zio_*:return
/self->in && self->ziostartts /
{
  self->zioendts = timestamp;
}
/* Time write is processed in the ZIO pipline end */

/* Outlier if too long in ZIO pipline */
fbt::zio_wait:return
/self->in && (timestamp - self->iostartts) >  ZIO_OUTLIER_THRESHOLD /
{
  self->toobig = 1;
}


/* Time pwrite is waiting for IO, very likely sync IO. */
fbt::zio_wait:entry
/self->in && self->zio_wait_startts == 0/
{
  self->zio_wait_startts = timestamp;
}

fbt::zio_wait:return
/self->in && self->zio_wait_startts/
{
  self->zio_wait = self->zio_wait + (timestamp - self->zio_wait_startts);
  self->zio_wait_startts = 0;
}

/* Get zpool name */
fbt::zio_create:return 
/self->in && args[1]->io_type/
{
  self->pool_name = stringof(args[1]->io_spa->spa_name)
}

syscall::pwrite:return
/self->in && self->toobig/
{
  this->e2e = timestamp - self->ts;
  this->zio_in = self->ziostartts - self->ts;
  this->zio_pipeline = self->zioendts - self->ziostartts;
  this->zio_out = timestamp - self->zioendts;

  @toobig[self->wts/1000000000, self->pool_name, curpsinfo->pr_psargs, pid, self->dev,
	       this->e2e/1000, this->zio_in/1000,
	       this->zio_pipeline/1000, self->zio_wait/1000, this->zio_out/1000] = count();


  outlier=1;
}
syscall::pwrite:return
/self->in/
{
  self->in = 0;
  self->ts = 0;
  self->wts = 0;
  self->iostartts = 0;
  self->dev = 0;
  self->toobig = 0;

  self->ziostartts = 0;
  self->zioendts = 0;
  self->zio_wait = 0;
  self->zio_wait_startts = 0;
  self->zio_wait_endts = 0;
  self->pool_name = "";
}
 
  
BEGIN
{ 
   outlier=0;
   header_print=0;
   printf("%Y\n", walltimestamp);
   printf(" TIMESTAMP               ZPOOL       PROCESS_NAME      PID                    FILE_NAME TOTAL_LATENCY ZIO_IN ZIO_PIPELINE ZIO_WAIT ZIO_OUT\n");
   printf(" ---------               -----       ------------      ---                    --------- ------------- ------ ------------ -------- -------\n");   
 }


tick-30sec
/header_print/
{
   printf("\n%Y\n", walltimestamp);
   printf(" TIMESTAMP               ZPOOL       PROCESS_NAME      PID                    FILE_NAME TOTAL_LATENCY ZIO_IN ZIO_PIPELINE ZIO_WAIT ZIO_OUT\n");
   printf(" ---------               -----       ------------      ---                    --------- ------------- ------ ------------ -------- -------\n");   
   header_print=0;
}
 
tick-5sec
/ outlier>0 /
{
 
  printa("%10d %19s %18s %8d %28s %13d \t%4d \t%4d \t%4d \t%4d\n",@toobig);
  trunc(@toobig);
  outlier=0;
  header_print=1;
}

