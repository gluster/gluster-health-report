from .utils import process_log_file

num_errors = 0


def callback_check_errors(pline):
    global num_errors, num_warning

    # Message IDs GD_MSG_VOL_VERS_MISMATCH, GD_MSG_CKSUM_VERS_MISMATCH,
    # GD_MSG_QUOTA_CONFIG_VERS_MISMATCH, GD_MSG_QUOTA_CONFIG_CKSUM_MISMATCH are
    # captured here
    if pline.log_level == "E" and (pline.msg_id == "106009" or
                                   pline.msg_id == "106010" or
                                   pline.msg_id == "106011" or
                                   pline.msg_id == "106012"):
        num_errors += 1


def report_check_version_or_cksum_errors_in_glusterd_log(ctx):
    process_log_file("/var/log/glusterfs/glusterd.log", callback_check_errors)

    if num_errors > 0:
        ctx.warning("version or cksum mismatch detected in Glusterd log file",
                    num_errors=num_errors)
