#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Philipp (University of Vienna)
#
# @Date: August 2018
#
# @Change History:
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Description:
#    Contains constant value parameter for flex_extract.
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import inspect

_VERSION_STR = '7.1'

# add path to pythonpath
PATH_LOCAL_PYTHON = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if PATH_LOCAL_PYTHON not in sys.path:
    sys.path.append(PATH_LOCAL_PYTHON)

PATH_FLEXEXTRACT_DIR = os.path.normpath(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')

PATH_TEMPLATES = os.path.join(PATH_FLEXEXTRACT_DIR + os.path.sep +
                              '_templates')

# path to gribtable
PATH_GRIBTABLE = os.path.join(PATH_TEMPLATES + os.path.sep +
                              'ecmwf_grib1_table_128')

PATH_RUN_DIR = os.path.join(PATH_FLEXEXTRACT_DIR + os.path.sep +
                                'run')

PATH_CONTROLFILES = os.path.join(PATH_RUN_DIR + os.path.sep +
                                'control')
