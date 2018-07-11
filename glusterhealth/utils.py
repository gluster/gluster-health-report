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
from logging import Logger, handlers
import sys
import time

from .rconf import rconf

RED = "\033[31m"
GREEN = "\033[32m"
ORANGE = "\033[33m"
NOCOLOR = "\033[0m"


def lf(event, **kwargs):
    """
    Log Format helper function, log messages can be
    easily modified to structured log format.
    lf("Config Change", sync_jobs=4, brick=/bricks/b1) will be
    converted as "Config Change<TAB>brick=/bricks/b1<TAB>sync_jobs=4"
    """
    msg = event
    for k, v in kwargs.items():
        msg += " {0}={1}".format(k, v)
    return msg


class GLogger(Logger):

    """Logger customizations for health checker.

    It implements a log format similar to that of glusterfs.
    """

    def makeRecord(self, name, level, *a):
        rv = Logger.makeRecord(self, name, level, *a)
        rv.nsecs = (rv.created - int(rv.created)) * 1000000
        fr = sys._getframe(4)
        callee = fr.f_locals.get('self')
        if callee:
            ctx = str(type(callee)).split("'")[1].split('.')[-1]
        else:
            ctx = '<top>'
        if not hasattr(rv, 'funcName'):
            rv.funcName = fr.f_code.co_name
        rv.lvlnam = logging.getLevelName(level)[0]
        rv.ctx = ctx
        return rv


LOGFMT = ("[%(asctime)s.%(nsecs)d] %(lvlnam)s [%(module)s{0}"
          ":%(lineno)s:%(funcName)s] %(ctx)s: %(message)s")


def setup_logging(level="INFO", label="", log_file=""):
    if label:
        label = "(" + label + ")"

    filename = None
    stream = None
    if log_file:
        if log_file in ('-', '/dev/stderr'):
            stream = sys.stderr
        elif log_file == '/dev/stdout':
            stream = sys.stdout
        else:
            filename = log_file

    datefmt = "%Y-%m-%d %H:%M:%S"
    fmt = LOGFMT.format(label)
    logging.root = GLogger("root", level)
    logging.setLoggerClass(GLogger)
    logging.Formatter.converter = time.gmtime  # Log in GMT/UTC time
    logging.getLogger().handlers = []
    logging.getLogger().setLevel(level)

    if filename is not None:
        logging_handler = handlers.WatchedFileHandler(filename)
        formatter = logging.Formatter(fmt=fmt,
                                      datefmt=datefmt)
        logging_handler.setFormatter(formatter)
        logging.getLogger().addHandler(logging_handler)
    else:
        logging.basicConfig(stream=stream,
                            format=fmt,
                            datefmt=datefmt,
                            level=level)


def color_txt(txt, color):
    return "%s%s%s" % (color, txt, NOCOLOR)


def _ok(for_log=False):
    txt = "[     OK]"
    if rconf.color_enabled and not for_log:
        return color_txt(txt, GREEN)
    return txt


def _notok(for_log=False):
    txt = "[ NOT OK]"
    if rconf.color_enabled and not for_log:
        return color_txt(txt, RED)
    return txt


def _warn(for_log=False):
    txt = "[WARNING]"
    if rconf.color_enabled and not for_log:
        return color_txt(txt, ORANGE)
    return txt


def _err(for_log=False):
    txt = "[  ERROR]"
    if rconf.color_enabled and not for_log:
        return color_txt(txt, RED)
    return txt


def _output(msg, **kwargs):
    for k, v in kwargs.items():
        msg += "  {0}={1}".format(k, v)

    return msg


def output_ok(msg, **kwargs):
    msg = _output(msg, **kwargs)
    logging.info("%s %s" % (_ok(for_log=True), msg))
    print("%s %s" % (_ok(), msg))


def output_notok(msg, **kwargs):
    msg = _output(msg, **kwargs)
    logging.error("%s %s" % (_notok(for_log=True), msg))
    print("%s %s" % (_notok(), msg))


def output_warning(msg, **kwargs):
    msg = _output(msg, **kwargs)
    logging.warn("%s %s" % (_warn(for_log=True), msg))
    print("%s %s" % (_warn(), msg))


def output_error(msg, **kwargs):
    msg = _output(msg, **kwargs)
    logging.error("%s %s" % (_err(for_log=True), msg))
    print("%s %s" % (_err(), msg))
