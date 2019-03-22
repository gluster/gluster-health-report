#
# Copyright (c) 2017 Red Hat, Inc.
#
# This file is part of gluster-health-report project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

import logging

from .utils import command_output, CommandError, byteorstr, strfrombytes

mem_used_limit = 90
gluster_mem_limit = 30


def report_system_memory_usage(ctx):
    cmd = "free -m"
    try:
        out = command_output(cmd)
        for line in out.split(byteorstr("\n")):
            if byteorstr("Mem") in line:
                memtype, total, used, free, shared, cache, available = \
                            line.split()
            elif byteorstr("Swap") in line:
                memtype, total, used, free = line.split()
            else:
                continue

            percent = int(100 * float(used)/float(total))
            if percent >= mem_used_limit:
                ctx.notok("Memory used percentage on system is at "
                          "alarming level",
                          memtype=memtype.strip(':'),
                          percentage=str(percent))
    except CommandError as err:
        ctx.notok("Failed to get memory usage")
        logging.warn(ctx.lf("free command failed",
                            error_code=err.message[0],
                            error=err.message[2]))


def report_gluster_memory_usage(ctx):
    cmd = ['pgrep', 'gluster']
    out = byteorstr("")
    try:
        out = command_output(cmd)
    except CommandError:
        ctx.notok("No gluster process running")
        return

    try:
        for pid in out.strip().split(byteorstr("\n")):
            mem_cmd = "ps -p {} -o %mem=,comm=".format(strfrombytes(pid))
            mem_out = command_output(mem_cmd)
            data = mem_out.strip().split(byteorstr(" "))
            mem_percent = strfrombytes(data[0].split(
                byteorstr('.'))[0].strip())
            proc_name = strfrombytes(data[1].strip())
            if int(mem_percent) >= gluster_mem_limit:
                ctx.notok("Memory used by gluster process is at "
                          "alarming level",
                          process_name=proc_name,
                          percentage=mem_percent)
            else:
                ctx.ok("Memory usage of gluster process",
                       process_name=proc_name,
                       percentage=mem_percent)
    except CommandError as err:
        ctx.notok("Failed to get memory usage of gluster processes")
        logging.warn(ctx.lf("pgrep/ps command failed",
                            error_code=err.message[0],
                            error=err.message[2]))
