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


def report_check_glusterd_uptime(ctx):
    cmd = "ps -C glusterd --no-header -o etimes"
    try:
        out = command_output(cmd)
        if int(out.strip()) < 86400:
            ctx.warning("Glusterd uptime is less than 24 hours",
                        uptime_sec=out.strip())
        else:
            ctx.ok("Glusterd is running", uptime_sec=out.strip())
    except CommandError as e:
        ctx.notok("Glusterd is not running")
        logging.warn(ctx.lf("Glusterd is not running",
                            error_code=e[0],
                            error=e[1]))
