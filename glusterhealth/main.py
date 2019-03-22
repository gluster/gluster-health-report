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

from __future__ import print_function
import logging
import time
from argparse import ArgumentParser
from datetime import datetime
import os
import sys
from subprocess import Popen, PIPE

from .utils import setup_logging, lf, output_ok, \
    output_notok, output_warning, output_error

from .rconf import rconf


PY3K = sys.version_info >= (3, 0)

reports_dir = os.path.join(
    os.path.dirname(__file__),
    "reports"
)


# Context to send to report functions
class Context(object):
    def __init__(self, conf):
        self.lf = lf
        self.ok = output_ok
        self.notok = output_notok
        self.warning = output_warning
        self.error = output_error
        self.conf = conf


def execute_bash_report(path, env):
    cmd = ["bash", path]
    p = Popen(cmd, stderr=PIPE, stdout=PIPE, env=env)
    out, err = p.communicate()
    if p.returncode == 0:
        for line in out.strip().split(b"\n"):
            print(line.decode() if PY3K else line)
    else:
        output_error("report error",
                     report=os.path.basename(path),
                     error=err.strip())


def main():
    # Most of the features need root permissions to run
    if (os.getuid() != 0):
        print("Only root can run this program. Become root or use sudo.")
        sys.exit(1)
    main_start_time = int(time.time())
    default_log_file = datetime.now().strftime(
        "gluster-health-report-%Y-%m-%d-%H-%M.log")

    parser = ArgumentParser()
    parser.add_argument("--log-dir", help="Log File dir",
                        default="/var/log/glusterfs/")
    parser.add_argument("--log-file", help="Log File",
                        default=default_log_file)
    parser.add_argument("--run-only",
                        help="List of reports to be run")
    parser.add_argument("--exclude",
                        help="List of reports to be excluded")

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

    # Included reports
    in_reports = []
    if rconf.args.run_only is not None:
        in_reports = rconf.args.run_only.split(",")
        in_reports = [p.strip() for p in in_reports]
    else:
        # If reports list not passed, include all reports exists in
        # reports directory
        ignore_list = ["utils.py", "__init__.py", "hello.py",
                       "utils.sh", "hello.sh"]
        for p in os.listdir(reports_dir):
            if not (p.endswith(".py") or p.endswith(".sh")) or \
               p in ignore_list:
                continue

            p = p.replace(".py", "").replace(".sh", "")
            in_reports.append(p)

    # Excluded reports list
    ex_reports = []
    if rconf.args.exclude is not None:
        ex_reports = rconf.args.exclude.split(",")
        ex_reports = [ep.strip() for ep in ex_reports]

    # If excluded reports list is not empty then remove the reports
    # from included lists
    if not ex_reports:
        reports = in_reports
    else:
        reports = []
        for p in in_reports:
            if p not in ex_reports:
                reports.append(p)

    rconf.enabled_reports = reports

    # If no reports found
    if not reports:
        print("No reports found")
        return

    # Logging setup
    setup_logging(log_file=rconf.log_file)

    # For bash scripts set env variable
    health_report_env = os.environ.copy()
    health_report_env["GLUSTER_HEALTH_REPORT_LOG_FILE"] = rconf.log_file

    py_reports = []
    sh_reports = []
    for p in set(reports):
        py_exists = sh_exists = 1

        if os.path.exists(os.path.join(reports_dir, p + ".py")):
            py_reports.append(p)
        else:
            py_exists = 0

        if os.path.exists(os.path.join(reports_dir, p + ".sh")):
            sh_reports.append(os.path.join(reports_dir, p + ".sh"))
        else:
            sh_exists = 0

        if py_exists == 0 and sh_exists == 0:
            print("WARNING: Report `%s' does not exist" % p)
            reports.remove(p)

    # Loaded reports summary
    print("\nLoaded reports: %s\n" % (
        ", ".join(reports) if reports else "None"))

    # Check each report, and execute the functions which starts with report_
    # TODO: All reports can be run in parallel
    for p in py_reports:
        # If include list sent by user is corrupt or report has some error
        try:
            pi = __import__("glusterhealth.reports." + p, fromlist=p)
        except ImportError as e:
            output_error("Unable to import report",
                         report=p, error=e)
            continue

        # Get list of all functions from the imported module
        all_funcs = dir(pi)
        for f in all_funcs:
            func = getattr(pi, f)
            # Execute all report functions which starts with report_
            if f.startswith("report_") and callable(func):
                logging.info(lf("Running report",
                                report=p, func=f, type="python"))
                num_reports += 1
                start_time = int(time.time())

                # Call the function with context as argument
                # In case of exception, log failure and also not_ok message
                try:
                    func(context)
                except Exception:
                    output_error("Report failure", report=f)
                    logging.exception(lf("Report failure", report=f))

                # Finished execution
                logging.info(lf("Finished execution of report function",
                                report=p,
                                func=f,
                                type="python",
                                duration_sec=int(time.time())-start_time))

    # Support for bash reports/reports
    for p in sh_reports:
        logging.info(lf("Running report", report=p, type="bash"))
        num_reports += 1
        start_time = int(time.time())

        # Execute the bash script
        execute_bash_report(p, health_report_env)

        # Finished execution
        logging.info(lf("Finished execution of report",
                        report=p,
                        type="bash",
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
