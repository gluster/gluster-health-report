import logging
import os

from .utils import command_output, CommandError


def get_mount_log_files():
    prefix = "/var/log/glusterfs/"
    logfiles = []
    for f in os.listdir(prefix):
        if f in ["glusterd.log", "cmd_history.log", "cli.log", "events.log"]:
            continue

        if f.startswith("gluster-health-report-"):
            continue

        if f.endswith(".log"):
            logfiles.append(os.path.join(f))
    return logfiles


def gfid__mismatch_dht(logfile, ctx):
    cmd = "grep 'gfid differs' " + logfile + " | grep -v grep | wc -l"
    try:
        out = command_output(cmd)
        if int(out.strip()) > 0:
            ctx.error("gfid mismatch found",
                      no_of_mismatches=out.strip())
        else:
            ctx.ok("No gfid mismatch", logfile=os.path.basename(logfile))
    except CommandError as err:
        ctx.notok("Command failure")
        logging.warn(ctx.lf("Command Failure",
                            error_code=err.message[0],
                            error=err.message[2]))


def report_gfid__mismatch_dht(ctx):
    logfiles = get_mount_log_files()
    for logfile in logfiles:
        gfid__mismatch_dht(logfile, ctx)
