#!/usr/bin/env python
# $Id$

##########################################################################
# Copyright (C) 2009 - 2014 Huygens ING & Gebrandy S.R.L.
# 
# This file is part of bioport.
# 
# bioport is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/gpl-3.0.html>.
##########################################################################


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

