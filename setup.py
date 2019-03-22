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

from setuptools import setup


setup(
    name="gluster-health-report",
    version="0.7",
    packages=["glusterhealth", "glusterhealth.reports"],
    include_package_data=True,
    install_requires=["glustercli"],
    entry_points={
        "console_scripts": [
            "gluster-health-report = glusterhealth.main:main"
        ]
    },
    platforms="linux",
    zip_safe=False,
    author="Gluster Developers",
    author_email="gluster-devel@gluster.org",
    description="Gluster Health Report tools",
    license="GPLv2",
    keywords="gluster, tool, health",
    url="https://github.com/gluster/gluster-health-report",
    long_description="""
    Gluster Health Report
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Environment :: Console",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
    ],
)
