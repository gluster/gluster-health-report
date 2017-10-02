from utils import process_log_file

GSYNCD_LOG_FILE = ("/var/log/glusterfs/geo-replication/gv1/"
                   "ssh%3A%2F%2Froot%40192.168.122.208%3Agluster"
                   "%3A%2F%2F127.0.0.1%3Agv2.log")

worker_restarts_data = {}


def filter_worker_restarts(line):
    if "starting gsyncd worker" in line:
        return True

    return False


def callback_worker_restarts(pline):
    global worker_restarts_data

    brick = pline.fields.get("brick", None)
    if brick is None:
        return

    # Counter initialize if not initialized for that brick
    if worker_restarts_data.get(brick, None) is None:
        worker_restarts_data[brick] = 0

    worker_restarts_data[brick] += 1


def report_check_worker_restarts(ctx):
    process_log_file(GSYNCD_LOG_FILE, callback_worker_restarts,
                     filter_worker_restarts)
    for k, v in worker_restarts_data.items():
        if v <= 1:
            ctx.ok("No Gsyncd worker restart", brick=k)
        else:
            ctx.warning("Gsyncd worker restarted more than once",
                        brick=k, num_restarts=v)
