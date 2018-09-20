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
# FILENAMES
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
FILE_NAMELIST = 'fort.4'
FILE_GRIB_INDEX = 'date_time_stepRange.idx'

# ------------------------------------------------------------------------------
#  PATHES
# ------------------------------------------------------------------------------

# path to the flex_extract directory
PATH_FLEXEXTRACT_DIR = os.path.normpath(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')

# path to the local python source files
PATH_LOCAL_PYTHON = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
PATH_RELATIVE_PYTHON = os.path.relpath(PATH_LOCAL_PYTHON, PATH_FLEXEXTRACT_DIR)
# add path to pythonpath
if PATH_LOCAL_PYTHON not in sys.path:
    sys.path.append(PATH_LOCAL_PYTHON)

# path to the templates
PATH_TEMPLATES = os.path.join(PATH_FLEXEXTRACT_DIR, '_templates')
PATH_RELATIVE_TEMPLATES = os.path.relpath(PATH_TEMPLATES, PATH_FLEXEXTRACT_DIR)

# path to the environment parameter file
PATH_ECMWF_ENV = os.path.join(PATH_LOCAL_PYTHON, FILE_USER_ENVVARS)
PATH_RELATIVE_ECMWF_ENV = os.path.relpath(PATH_ECMWF_ENV, PATH_FLEXEXTRACT_DIR)

# path to gribtable
PATH_GRIBTABLE = os.path.join(PATH_TEMPLATES, 'ecmwf_grib1_table_128')

# path to run directory
PATH_RUN_DIR = os.path.join(PATH_FLEXEXTRACT_DIR, 'run')
PATH_RELATIVE_RUN_DIR = os.path.relpath(PATH_RUN_DIR, PATH_FLEXEXTRACT_DIR)

# path to directory where all control files are stored
PATH_CONTROLFILES = os.path.join(PATH_RUN_DIR, 'control')
PATH_RELATIVE_CONTROLFILES = os.path.relpath(PATH_CONTROLFILES, PATH_FLEXEXTRACT_DIR)

# path to directory where all job scripts are stored
PATH_JOBSCRIPTS = os.path.join(PATH_RUN_DIR, 'jobscripts')
PATH_RELATIVE_JOBSCRIPTS = os.path.relpath(PATH_JOBSCRIPTS, PATH_FLEXEXTRACT_DIR)

# path to the fortran executable and the source code
PATH_FORTRAN_SRC = os.path.join(PATH_FLEXEXTRACT_DIR, 'src')
PATH_RELATIVE_FORTRAN_SRC = os.path.relpath(PATH_FORTRAN_SRC, PATH_FLEXEXTRACT_DIR)

# path to the python testing directory
PATH_TEST_DIR = os.path.join(PATH_LOCAL_PYTHON, 'pythontest')

