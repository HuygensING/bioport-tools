#!/usr/bin/env python
# $Id$

from setuptools import setup

__version__ = "0.1.3dev"

setup(
    name="gerbrandyutils",
    version=__version__,
    description='utility functions and classes common to all projects',
    packages=['gerbrandyutils'],
    install_requires=["psyco"],
    )

