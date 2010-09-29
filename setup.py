#!/usr/bin/env python
# $Id$

from setuptools import setup

__version__ = "0.1.3dev"

setup(
    name="gerbrandyutils",
    version=__version__,
    description='utility functions and classes common to all projects',
    packages=['gerbrandyutils'],
# commented as it doesn't get installed on 64 bit sytsems
#    install_requires=["psyco"],
    )

