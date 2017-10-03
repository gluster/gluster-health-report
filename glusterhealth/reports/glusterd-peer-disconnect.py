from utils import process_log_file

num_errors = 0


def callback_check_errors(pline):
    global num_errors 

    if pline.log_level == "E" and pline.msg_id == "106004":
        num_errors += 1


def report_check_errors_in_glusterd_log(ctx):
    process_log_file("/var/log/glusterfs/glusterd.log", callback_check_errors)

    if num_errors > 0:
        ctx.warning("peer disconnect num_errors in Glusterd log file", num_errors=num_errors)

