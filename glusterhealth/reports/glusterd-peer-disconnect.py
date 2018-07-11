import logging

from .utils import command_output, CommandError
from .utils import process_log_file

num_errors = 0


def callback_check_errors(pline):
    global num_errors

    if pline.log_level == "E" and pline.msg_id == "106004":
        num_errors += 1


def report_check_errors_in_glusterd_log(ctx):
    process_log_file("/var/log/glusterfs/glusterd.log", callback_check_errors)

    if num_errors > 0:
        ctx.warning("peer disconnect num_errors in Glusterd log file",
                    num_errors=num_errors)


def report_peer_disconnect(ctx):
    cmd = "gluster peer status"
    try:
        out = command_output(cmd)
        peer_count = out.split("\n")[0].split(":")[1].strip()
        peer_conn_count = out.count("(Connected)")
        dis_count = int(peer_count) - int(peer_conn_count)
        if 0 < dis_count:
            ctx.notok("One or more peer/s in disconnected/rejected state",
                      total_peer_count=int(peer_count),
                      disconnected_rejected_count=dis_count)
            logging.warning("Peer status: \n" + out)
        else:
            ctx.ok("All peers are in connected state",
                   total_peer_count=int(peer_count),
                   connected_count=int(peer_conn_count))
    except CommandError as e:
        ctx.notok("Failed to check peer status")
        logging.warn(ctx.lf("peer status command failed",
                            error_code=e[0],
                            error=e[1]))
