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


def report_hello(ctx):
    ctx.ok("CPU Usage")
    ctx.ok("Network Health")
    ctx.warning("Disconnect events")
    ctx.warning("Memory Usage")
    ctx.notok("Log rotate setup")
    ctx.ok("Error logs in last day")
    ctx.warning("Changelog size")
