import logging

num_panic = 0
num_locks = 0

def report_kernel_issues(ctx):
    global num_locks, num_panic
    with open("/var/log/messages", "r") as fp:
        for line in fp:
            if "BUG: soft lockup" in line:
                num_locks+=1
            if "Kernel panic" in line:
                num_panic+=1
    if num_locks > 0:
        ctx.error("CPU stuck with soft locks", num_locks=num_locks)
    if num_panic > 0:
        ctx.error("Kernel Panic", num_panic=num_panic)



