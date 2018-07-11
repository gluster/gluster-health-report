import datetime

from .utils import process_log_file

num_errors = 0
num_warning = 0


def callback_check_errors(pline):
    global num_errors, num_warning
    if pline.ts is None:
        return
    pl = datetime.datetime.strptime(pline.ts, "%Y-%m-%d %H:%M:%S.%f")
    t = datetime.datetime.now() - datetime.timedelta(hours=23)
    if pl > t:
        if pline.log_level == "E":
            num_errors += 1

        if pline.log_level == "W":
            num_warning += 1


def report_check_errors_in_glusterd_log(ctx):
    process_log_file("/var/log/glusterfs/glusterd.log", callback_check_errors)

    if num_errors > 0:
        ctx.warning("Errors in Glusterd log file", num_errors=num_errors)

    if num_warning > 0:
        ctx.warning("Warnings in Glusterd log file",
                    num_warning=num_warning)
