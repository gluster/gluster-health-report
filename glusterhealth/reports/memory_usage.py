#
# Copyright (c) 2017 Red Hat, Inc.
#
# This file is part of gluster-health-report project which is a
# subproject of GlusterFS ( www.gluster.org)
#
# This file is licensed to you under your choice of the GNU Lesser
# General Public License, version 3 or any later version (LGPLv3 or
# later), or the GNU General Public License, version 2 (GPLv2), in all
# cases as published by the Free Software Foundation.

import logging

from utils import command_output, CommandError

mem_used_limit = 90
gluster_mem_limit = 30
	
def report_system_memory_usage(ctx):
	cmd = "free -m"
	try:
		out = command_output(cmd)
		for line in out.split("\n"):
			if "Mem" in line:
				memtype, total, used, free, shared, cache, available = \
							line.split()
	 		elif "Swap" in line:
				memtype, total, used, free = line.split()
			else:
				continue

			percent = int(100 * float(used)/float(total))
			if percent >= mem_used_limit:
				ctx.notok("Memory used percentage on system is at alarming level", memtype=memtype.strip(':'), percentage=str(percent))
	except CommandError as e:
		ctx.notok("Failed to get memory usage")
		logging.warn(ctx.lf("free command failed",
							error_code=e[0],
							error=e[1]))

def report_gluster_memory_usage(ctx):
	cmd = ['pgrep','gluster']
	try:
		out = command_output(cmd)
		for pid in out.strip().split("\n"):
			mem_cmd = "ps -p {} -o %mem".format(pid)
			mem_out = command_output(mem_cmd)
			mem_percent = mem_out.split('\n')[1].split('.')[0].strip()
			if int(mem_percent) >= gluster_mem_limit:
				proc_cmd = "ps -p {} -o comm=".format(pid)
				proc_out = command_output(proc_cmd)
				ctx.notok("Memory used by gluster process is at alarming level", process_name=proc_out.strip(), percentage=mem_percent)
	except CommandError as e:
		ctx.notok("Failed to get memory usage of gluster processes")
		logging.warn(ctx.lf("pgrep/ps command failed",
							error_code=e[0],
							error=e[1]))
