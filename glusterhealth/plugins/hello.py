def report_hello(ctx):
    ctx.ok("CPU Usage")
    ctx.ok("Network Health")
    ctx.warning("Disconnect events")
    ctx.warning("Memory Usage")
    ctx.notok("Log rotate setup")
    ctx.ok("Error logs in last day")
    ctx.warning("Changelog size")
