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

# ------------------------------------------------------------------------------
# EXPLICIT FILENAMES
# ------------------------------------------------------------------------------

FLEXEXTRACT_DIRNAME = 'flex_extract_v' + _VERSION_STR
FILE_MARS_REQUESTS = 'mars_requests.dat'
FORTRAN_EXECUTABLE = 'CONVERT2'
FILE_USER_ENVVARS = 'ECMWF_ENV'
TEMPFILE_INSTALL_COMPILEJOB = 'compilejob.temp'
FILE_INSTALL_COMPILEJOB = 'compilejob.ksh'
TEMPFILE_INSTALL_JOB = 'job.temp.o'
TEMPFILE_JOB = 'job.temp'
FILE_JOB_OD = 'job.ksh'
FILE_JOB_OP = 'jopoper.ksh'

# ------------------------------------------------------------------------------
# EXPLICIT PATHES
# ------------------------------------------------------------------------------

# add path to pythonpath
PATH_LOCAL_PYTHON = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if PATH_LOCAL_PYTHON not in sys.path:
    sys.path.append(PATH_LOCAL_PYTHON)

PATH_FLEXEXTRACT_DIR = os.path.normpath(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')

PATH_RELATIVE_PYTHON = os.path.relpath(PATH_LOCAL_PYTHON, PATH_FLEXEXTRACT_DIR)

PATH_TEMPLATES = os.path.join(PATH_FLEXEXTRACT_DIR + os.path.sep +
                              '_templates')

PATH_RELATIVE_TEMPLATES = os.path.relpath(PATH_TEMPLATES, PATH_FLEXEXTRACT_DIR)

# path to gribtable
PATH_GRIBTABLE = os.path.join(PATH_TEMPLATES + os.path.sep +
                              'ecmwf_grib1_table_128')

# path to run directory
PATH_RUN_DIR = os.path.join(PATH_FLEXEXTRACT_DIR + os.path.sep +
                            'run')

# path to directory where all control files are stored
PATH_CONTROLFILES = os.path.join(PATH_RUN_DIR + os.path.sep +
                                 'control')

# path to directory where all control files are stored
PATH_JOBSCRIPTS = os.path.join(PATH_RUN_DIR + os.path.sep +
                               'jobscripts')

PATH_FORTRAN_SRC = os.path.join(PATH_FLEXEXTRACT_DIR + os.path.sep +
                                'src')

PATH_RELATIVE_FORTRAN_SRC = os.path.relpath(PATH_FORTRAN_SRC, PATH_FLEXEXTRACT_DIR)

