gluster_binaries = {'glusterfsd', 'glusterd', 'glusterfs'}

num_panic = 0
num_locks = 0


def report_kernel_issues(ctx):
    global num_locks, num_panic
    with open("/var/log/messages", "r") as fp:
        for line in fp:
            if "BUG: soft lockup" in line:
                num_locks += 1
            if "Kernel panic" in line:
                num_panic += 1
    if num_locks > 0:
        ctx.error("CPU stuck with soft locks", num_locks=num_locks)
    if num_panic > 0:
        ctx.error("Kernel Panic", num_panic=num_panic)


def report_gluster_hung_task(ctx):
    gldict = dict.fromkeys(gluster_binaries, 0)
    with open("/var/log/messages", "r") as fp:
        for line in fp:
            if "blocked for more than 120 seconds" in line:
                task_hung_str = line.strip().split('INFO')[1]
                task_hung = task_hung_str.strip().split(':')[1]
                task_name = task_hung.strip().split(' ')[1]
                if task_name in gluster_binaries:
                    gldict[task_name] = gldict[task_name] + 1

    for task_name, times in gldict.iteritems():
        if times > 0:
            ctx.error("Gluster process was hung/blocked for more than "
                      "120 seconds",
                      process=task_name, times=times)
