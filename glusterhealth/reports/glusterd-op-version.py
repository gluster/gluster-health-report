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


def report_check_glusterd_op_version(ctx):
    cmd1 = "gluster v get all cluster.op-version"
    cmd2 = "gluster v get all cluster.max-op-version"
    try:
        out1 = command_output(cmd1)
        out2 = command_output(cmd2)
        version1 = out1.split()[-1]
        version2 = out2.split()[-1]
        if version1 != version2:
            ctx.warning("op-version is not up to date")
        else:
            ctx.ok("op-version is up to date", op_version=version1,
                   max_op_version=version2)
    except CommandError as e:
        ctx.notok("Failed to check op-version")
        logging.warn(ctx.lf("Failed to check op-version",
                            error_code=e[0],
                            error=e[1]))
