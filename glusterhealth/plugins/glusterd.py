import logging

from utils import command_output, CommandError


def report_check_running(ctx):
    cmd = ["ps", "-C", "glusterd"]
    try:
        command_output(cmd)
        ctx.ok("Glusterd is running")
    except CommandError as e:
        ctx.notok("Glusterd is not running")
        logging.warn(ctx.lf("Glusterd is not running",
                            error_code=e[0],
                            error=e[1]))
