#
# Copyright (c) 2017 Red Hat, Inc.
#
# This file is part of libgfapi-python project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

import logging
import time
from argparse import ArgumentParser
from datetime import datetime
import os

from utils import setup_logging, lf, output_ok, \
    output_notok, output_warning, output_error

from rconf import rconf


# Context to send to plugin functions
class Context(object):
    def __init__(self, conf):
        self.lf = lf
        self.ok = output_ok
        self.notok = output_notok
        self.warning = output_warning
        self.error = output_error
        self.conf = conf


def main():
    main_start_time = int(time.time())
    default_log_file = datetime.now().strftime(
        "gluster-health-report-%Y-%m-%d-%H-%M.log")

    parser = ArgumentParser()
    parser.add_argument("--log-dir", help="Log File dir",
                        default="/var/log/glusterfs/")
    parser.add_argument("--log-file", help="Log File",
                        default=default_log_file)
    parser.add_argument("--include",
                        help="List of plugins to be included in the report")
    parser.add_argument("--exclude",
                        help="List of plugins to be excluded from the report")

    rconf.args = parser.parse_args()

    # If stdout or stderr
    if rconf.args.log_file in ("-", "/dev/stdout", "/dev/stderr"):
        rconf.log_file = rconf.args.log_file
    else:
        rconf.log_file = os.path.join(
            rconf.args.log_dir,
            rconf.args.log_file
        )

    # For printing final summary
    num_reports = 0

    # Context to send to each report func call
    context = Context(rconf)

    # Included plugins
    in_plugins = []
    if rconf.args.include is not None:
        in_plugins = rconf.args.include.split(",")
        in_plugins = [p.strip() for p in in_plugins]
    else:
        # If plugins list not passed, include all plugins exists in
        # plugins directory
        plugins_dir = os.path.join(
            os.path.dirname(__file__),
            "plugins"
        )
        for p in os.listdir(plugins_dir):
            if not p.endswith(".py") or (p in ["utils.py",
                                               "__init__.py",
                                               "hello.py"]):
                continue

            p = p.replace(".py", "")
            in_plugins.append(p)

    # Excluded plugins list
    ex_plugins = []
    if rconf.args.exclude is not None:
        ex_plugins = rconf.args.exclude.split(",")
        ex_plugins = [ep.strip() for ep in ex_plugins]

    # If excluded plugins list is not empty then remove the plugins
    # from included lists
    if not ex_plugins:
        plugins = in_plugins
    else:
        plugins = []
        for p in in_plugins:
            if p not in ex_plugins:
                plugins.append(p)

    rconf.enabled_plugins = plugins

    # If no plugins found
    if not plugins:
        print("No reports found")
        return

    # Logging setup
    setup_logging(log_file=rconf.log_file)

    # Loaded plugins summary
    print("Loaded plugins: %s\n" % (
        ", ".join(plugins) if plugins else "None"))

    # Check each plugin, and execute the functions which starts with report_
    # TODO: All reports can be run in parallel
    for p in plugins:
        # If include list sent by user is corrupt or plugin has some error
        try:
            pi = __import__("glusterhealth.plugins." + p, fromlist=p)
        except ImportError as e:
            output_error("Unable to import plugin",
                         plugin=p, error=e)
            continue

        # Get list of all functions from the imported module
        all_funcs = dir(pi)
        for f in all_funcs:
            func = getattr(pi, f)
            # Execute all report functions which starts with report_
            if f.startswith("report_") and callable(func):
                logging.info(lf("Running report",
                                plugin=p, func=f))
                num_reports += 1
                start_time = int(time.time())

                # Call the function with context as argument
                # In case of exception, log failure and also not_ok message
                try:
                    func(context)
                except:
                    output_error("Report failure", report=f)

                # Finished execution
                logging.info(lf("Finished execution of report function",
                                plugin=p,
                                func=f,
                                duration_sec=int(time.time())-start_time))

    # Log some metrics
    logging.info(lf("Completed Gluster Health check",
                    duration_sec=int(time.time())-main_start_time,
                    number_of_reports=num_reports))

    # Print message for log file location
    if rconf.log_file not in ("-", "/dev/stderr", "/dev/stdout"):
        print("\n....")
        print("You can find the detailed health-report"
              "at %s\n" % rconf.log_file)


if __name__ == "__main__":
    main()
