# CONTRIBUTING

## Setup

1. Fork [this](https://github.com/aravindavk/gluster-health-report)
   repository on github
2. Add your fork as a git remote:

        git remote add fork https://github.com/<your-github-username>/gluster-health-report

## Code contribution workflow

This repository currently follows GitHub's
[Fork & Pull](https://help.github.com/articles/about-pull-requests/)
workflow for code contributions.

Here is a short guide on how to work on a new patch. In this example,
we will work on a patch called hellopatch

    $ git checkout master
    $ git pull
    $ git checkout -b hellopatch

Do your work here and commit. Once you are ready to push, you will
type the following

    $ git push fork hellopatch

## Creating A Pull Request

When you are satisfied with your changes, you will then need to go to
your repo in GitHub.com and create a pull request for your branch.
Your pull request will be reviewed and merged.

## Build and Test
`setup.py develop` installs only meta information, so that all the
changes you make to your repository will be immediately reflected
without installing again.

    cd gluster-health-report
    sudo python setup.py develop

Now you are ready to run `gluster-health-report`

## Add a Python report
If you are interested in contributing new report in Python, create a
new file in `$SRC/glusterhealth/reports` directory. For example, `restart_finder.py`

Any function which starts with `report_` will be called by the
framework. A very simple plugin can be as follows

    def report_glusterd_restart_find(ctx):
        ctx.ok("No restarts")

Plugin function gets a Context which provides following utility
functions

    ctx.lf - Format the log message in structured logging format
    ctx.ok - Send a OK summary message back to framework
    ctx.error - Send error summary message back to framework
    ctx.notok - Send notok summary message back to framework
    ctx.warning - Send warning summary message back to framework
    ctx.rconf - Runtime configurations set by framework
        ctx.rconf.log_file - Log file path
        ctx.rconf.args - Parsed Arguments namespace
        ctx.rconf.enabled_reports - List of enabled reports, useful if
            any inter dependency

Logging is also very simple, just import `logging` and start using
`logging.info`, `logging.warning` etc without requiring any setup.

Log parsing utility is available to parse the log lines and call the
registered callback function. Check
`$SRC/glusterhealth/reports/errors_in_logs.py` file for more
information about its use.

Example,

    import logging

    from utils import command_output, CommandError


    def report_check_glusterd_uptime(ctx):
        cmd = "ps -C glusterd --no-header -o etimes"
        try:
            out = command_output(cmd)
            if out.strip() < "86400":
                ctx.warning("Glusterd uptime is less than 24 hours",
                            uptime_sec=out.strip())
            else:
                ctx.ok("Glusterd is running", uptime_sec=out.strip())
        except CommandError as e:
            ctx.notok("Glusterd is not running")
            logging.warn(ctx.lf("Glusterd is not running",
                                error_code=e[0],
                                error=e[1]))

## Add a Bash report
To add reports in Bash, create a new file in
`$SRC/glusterhealth/reports` directory. For example,
`restart_finder.sh`

Include utils as,

    . $(dirname $(readlink -e $0))/utils.sh

Following functions are available to send summary back to the
framework

    OK - Send OK summary message to framework
    NOTOK - Send NOTOK summary message to framework
    WARNING - Send WARNING summary message to framework
    ERROR - Send ERROR summary message to framework
    LOGINFO - Log INFO message
    LOGERROR - Log ERROR message
    LOGWARNING - Log WARNING message
    LOGDEBUG - Log DEBUG message

Example,

    . $(dirname $(readlink -e $0))/utils.sh

    out=$(grep " E " /var/log/glusterfs/glusterd.log | grep -v grep | wc -l)

    if [ $out -gt 0 ]; then
        WARNING Errors in Glusterd log file num_errors=$out
    fi

    out=$(grep " W " /var/log/glusterfs/glusterd.log | grep -v grep | wc -l)

    if [ $out -gt 0 ]; then
        WARNING Warnings in Glusterd log file num_warnings=$out
    fi
