import logging

from .utils import process_log_file

from gluster.cli import volume, georep


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


def report_non_participating_bricks(ctx):
    bricks_status = {}
    non_participating_bricks = []
    volinfo = volume.status_detail()
    georep_status = georep.status()
    for v in volinfo:
        for b in v["bricks"]:
            bricks_status[b["name"]] = b["online"]

    for session in georep_status:
        for conn in session:
            if bricks_status[conn["master_node"] + ":" +
                             conn["master_brick"]] and \
                             conn["status"] == "Offline":
                non_participating_bricks.append(conn["master_node"] + ":" +
                                                conn["master_brick"])

        if non_participating_bricks:
            ctx.notok("New bricks added to volume but not added to geo-rep. "
                      "Needs action!!!")
            logging.error(ctx.lf("Bricks not added to geo-rep. "
                                 "Take below action.",
                                 bricks=non_participating_bricks))
            logging.info(ctx.lf("---ADD BRICK TO GEOREP-----"))
            logging.info(ctx.lf("1. gluster system:: exec gsec_create"))
            logging.info(ctx.lf("2. gluster volume geo-rep <mastervol> "
                                "<slavehost>::<slavevol> create push-pem "
                                "force"))
            logging.info(ctx.lf("3. gluster volume geo-rep <mastervol> "
                                "<slavehost>::<slavevol> start force"))
            logging.info(ctx.lf("----------------------------"))
