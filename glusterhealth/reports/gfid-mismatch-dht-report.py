import logging

from .utils import command_output, CommandError


logfile = "/var/log/glusterfs/mnt.log"


def report_gfid__mismatch_dht(ctx):
    cmd = "grep 'gfid differs' " + logfile + " | grep -v grep | wc -l"
    try:
        out = command_output(cmd)
        if int(out.strip()) > 0:
            ctx.error("gfid mismatch found",
                      no_of_mismatches=out.strip())
        else:
            ctx.ok("no gfid mismatch")
    except CommandError as e:
        ctx.notok("Command failure")
        logging.warn(ctx.lf("Command Failure",
                            error_code=e[0],
                            error=e[1]))
