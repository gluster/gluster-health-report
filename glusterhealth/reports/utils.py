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
import re
from subprocess import Popen, PIPE


class CommandError(Exception):
    pass


def command_output(cmd):
    shell = True if isinstance(cmd, str) else False
    p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=shell)
    out, err = p.communicate()
    if p.returncode != 0:
        raise CommandError(p.returncode, err.strip())

    return out


# [TS] LOG_LEVEL [MSGID: <ID>] [FILE:LINE:FUNC] DOMAIN: MSG
# MSGID is optional and MSG can be structured log format or can be normal msg
log_pattern = re.compile('\[([^\]]+)\]\s'
                         '([IEWTD])\s'
                         '(\[MSGID:\s([^\]]+)\]\s)?'
                         '\[([^\]]+)\]\s'
                         '([^:]+):\s'
                         '(.+)')


class ParsedData(object):
    def __init__(self):
        self.known_format = False
        self.ts = None
        self.log_level = None
        self.msg_id = None
        self.file_info = None
        self.domain = None
        self.message = None
        self.fields = []

    def __str__(self):
        data = (
            "Known Format: {0}\n"
            "Timestamp   : {1}\n"
            "Log Level   : {2}\n"
            "MSG ID      : {3}\n"
            "File Info   : {4}\n"
            "Domain      : {5}\n"
            "Message     : {6}\n".format(
                self.known_format,
                self.ts,
                self.log_level,
                self.msg_id,
                self.file_info,
                self.domain,
                self.message
            ))
        if self.fields:
            data += "\nFields      : "
            for k, v in self.fields.items():
                data += "{0}={1}, ".format(k, v)

        data = data.strip(", ")
        return data


def parse_log_line(data):
    m = log_pattern.match(data)
    out = ParsedData()
    if m:
        out.known_format = True
        out.ts = m.group(1)
        out.log_level = m.group(2)
        out.msg_id = m.group(4)
        out.file_info = m.group(5)
        out.domain = m.group(6)

        msg_parts = m.group(7).split("\t")
        out.message = msg_parts[0]

        out.fields = {}
        if (len(msg_parts) > 1):
            for i in range(1, len(msg_parts)):
                key_value = msg_parts[i].split("=")
                # If no value, then this will be same as key
                out.fields[key_value[0]] = key_value[-1]
    else:
        # Add raw message to message, Note: known_format is False
        out.message = data

    return out


def process_log_file(path, callback, filterfunc=lambda l: True):
    with open(path) as f:
        for line in f:
            if filterfunc(line):
                pline = parse_log_line(line)
                callback(pline)


class DiskUsage(object):
    def __init__(self, device, size, used, available, percentage, mountpoint):
        self.device = device
        self.size = size
        self.used = used
        self.available = available
        self.percentage = percentage
        self.mountpoint = mountpoint


def get_disk_usage_details(path, ctx):
    if path is None:
        return
    cmd = ["df", path]
    try:
        out = command_output(cmd)
        device, size, used, available, percentage, mountpoint = \
            out.split("\n")[1].split()

        return DiskUsage(device, size, used, available, percentage, mountpoint)
    except CommandError as e:
        logging.warning("Disk usage: \n" + out)
        logging.warn(ctx.lf("disk usage failed",
                     error_code=e[0],
                     error=e[1]))
    return None
