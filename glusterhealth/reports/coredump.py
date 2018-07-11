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

from .utils import command_output, CommandError


def report_coredump(ctx):
    cmd = "ulimit -c"
    try:
        out = command_output(cmd)
        if out.strip() == "unlimited":
            ctx.ok("The maximum size of core files created is set to "
                   "unlimted.")
        else:
            ctx.notok("The maximum size of core files created is NOT set "
                      "to unlimited.")
    except CommandError as e:
        ctx.notok("ulimit check failed")
        logging.warn(ctx.lf("ulimit check failed",
                            error_code=e[0],
                            error=e[1]))
