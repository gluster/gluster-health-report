# Gluster Health Report Tool

Use this tool to analyze the Gluster node for correctness or health.

## Usage

    gluster-health-report

or run `gluster-health-report --help` for more details.

## Install

Clone the repo and install using,

    git clone
    cd gluster-health-report
    sudo python setup.py install

## How to add new report
Adding new report is very simple, add a python file in
`$SRC/plugins/myplugin.py` and implement your report. Any function
which starts with the name "report_" will be executed by the health
checker framework.

Following example shows a report which checks Glusterd is running or
not.

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


To understand the plugin implementation, let us walk through line by
line

Import logging library to use logging in your report/plugin. Note:
Logging setup stuff is already taken care by the framework itself.

    import logging

Import utility functions provided by the framework to execute the
command.

    from utils import command_output, CommandError

Implement your report

    def report_check_running(ctx):

Executing ps command to check glusterd is running or not

        cmd = ["ps", "-C", "glusterd"]

If command returns zero/success, send message to framework using
`ctx.ok`

        try:
            command_output(cmd)
            ctx.ok("Glusterd is running")

If command fails then send message to framework using `ctx.notok`.
Also add entry to log file with additional details.

        except CommandError as e:
            ctx.notok("Glusterd is not running")
            logging.warn(ctx.lf("Glusterd is not running",
                                error_code=e[0],
                                error=e[1]))

## Run Context
Each report function should accept context argument, which provides
following methods.

    ctx.lf - Format the log message in structured logging format
    ctx.ok - Send a OK summary message back to framework
    ctx.error - Send error summary message back to framework
    ctx.notok - Send notok summary message back to framework
    ctx.warning - Send warning summary message back to framework
    ctx.rconf - Runtime configurations set by framework
        ctx.rconf.log_file - Log file path
        ctx.rconf.args - Parsed Arguments namespace
        ctx.rconf.enabled_plugins - List of enabled plugins, useful if
            any inter dependency

## Dummy plugin
A dummy plugin is added, which just prints some messages without
inspecting any health.

    def report_hello(ctx):
        ctx.ok("CPU Usage")
        ctx.ok("Network Health")
        ctx.warning("Disconnect events")
        ctx.warning("Memory Usage")
        ctx.notok("Log rotate setup")
        ctx.ok("Error logs in last day")
        ctx.warning("Changelog size")

For testing it can be executed using

    gluster-health-report --log-dir . --include hello

Output:

    Loaded plugins: hello
    ....
     
    [     OK] CPU Usage
    [     OK] Network Health
    [WARNING] Disconnect events
    [WARNING] Memory Usage
    [ NOT OK] Log rotate setup
    [     OK] Error logs in last day
    [WARNING] Changelog size
     
    ....
    You can find the detailed health-report at ./gluster-health-report-2017-09-20-16-54.log
