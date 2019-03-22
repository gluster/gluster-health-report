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


def report_check_firewall_ports(ctx):
    cmd = "netstat -npl | grep 24007 | grep -i glusterd"
    cmd1 = "netstat -npl | grep -n /glusterfsd | grep tcp"
    try:
        out = command_output(cmd)
        out1 = command_output(cmd1)

        if out:
            ctx.ok("Ports open for glusterd:\n" + out)
        else:
            ctx.warning("Unable to find ports for glusterd")

        logging.warning("Firewall status of glusterd: \n" + out)

        if out1:
            ctx.ok("Ports open for glusterfsd:\n" + out1)
        else:
            ctx.warning("Unable to find ports for glusterfsd")

        logging.warning("Firewall status of glusterfsd: \n" + out1)
    except CommandError as err:
        ctx.notok("some error with firewall check")
        logging.warn(ctx.lf("firewall check error",
                            error_code=err.message[0],
                            error=err.message[2]))
