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

FILE_MARS_REQUESTS = 'mars_requests.csv'
FORTRAN_EXECUTABLE = 'CONVERT2'
TEMPFILE_USER_ENVVARS = 'ECMWF_ENV.template'
FILE_USER_ENVVARS = 'ECMWF_ENV'
TEMPFILE_INSTALL_COMPILEJOB = 'compilejob.template'
FILE_INSTALL_COMPILEJOB = 'compilejob.ksh'
TEMPFILE_INSTALL_JOB = 'job.temp.o'
TEMPFILE_JOB = 'job.temp'
FILE_JOB_OD = 'job.ksh'
FILE_JOB_OP = 'jopoper.ksh'
FILE_NAMELIST = 'fort.4'
FILE_GRIB_INDEX = 'date_time_stepRange.idx'
FILE_GRIBTABLE = 'ecmwf_grib1_table_128'

# ------------------------------------------------------------------------------
# DIRECTORY NAMES
# ------------------------------------------------------------------------------

FLEXEXTRACT_DIRNAME = 'flex_extract_v' + _VERSION_STR
INPUT_DIRNAME_DEFAULT = 'workspace'

# ------------------------------------------------------------------------------
#  PATHES
# ------------------------------------------------------------------------------

# path to the local python source files
# first thing to get because the submitted python script starts in here
PATH_LOCAL_PYTHON = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
# add path to pythonpath
if PATH_LOCAL_PYTHON not in sys.path:
    sys.path.append(PATH_LOCAL_PYTHON)
PATH_FLEXEXTRACT_DIR = os.path.normpath(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../../')
PATH_RUN_DIR = os.path.join(PATH_FLEXEXTRACT_DIR, 'run')
PATH_SOURCES = os.path.join(PATH_FLEXEXTRACT_DIR, 'source')
PATH_TEMPLATES = os.path.join(PATH_FLEXEXTRACT_DIR, 'templates')
PATH_ECMWF_ENV = os.path.join(PATH_RUN_DIR, FILE_USER_ENVVARS)
PATH_GRIBTABLE = os.path.join(PATH_TEMPLATES, FILE_GRIBTABLE)
PATH_JOBSCRIPTS = os.path.join(PATH_RUN_DIR, 'jobscripts')
PATH_FORTRAN_SRC = os.path.join(PATH_SOURCES, 'fortran')
PATH_TEST_DIR = os.path.join(PATH_SOURCES, 'pythontest')
PATH_INPUT_DIR = os.path.join(PATH_RUN_DIR, INPUT_DIRNAME_DEFAULT)
if os.getenv('CONTROL') and '/' in os.getenv('CONTROL'):
    # this is only needed if remote version with job script is used!
    # because job is directly submitted from SCRATCH and because the
    # CONTROL file is stored there, the normal path is not valid.
    PATH_CONTROLFILES = os.getenv('CONTROL')
else:
    PATH_CONTROLFILES = os.path.join(PATH_RUN_DIR, 'control')
#
# ------------------------------------------------------------------------------
# for making the installation tar ball, the relative pathes to the
# flex_extract root directory are needed
# ------------------------------------------------------------------------------

PATH_REL_PYTHON = os.path.relpath(PATH_LOCAL_PYTHON, PATH_FLEXEXTRACT_DIR)
PATH_REL_CONTROLFILES = os.path.relpath(PATH_CONTROLFILES, PATH_FLEXEXTRACT_DIR)
PATH_REL_TEMPLATES = os.path.relpath(PATH_TEMPLATES, PATH_FLEXEXTRACT_DIR)
PATH_REL_ECMWF_ENV = os.path.relpath(PATH_ECMWF_ENV, PATH_FLEXEXTRACT_DIR)
PATH_REL_RUN_DIR = os.path.relpath(PATH_RUN_DIR, PATH_FLEXEXTRACT_DIR)
PATH_REL_JOBSCRIPTS = os.path.relpath(PATH_JOBSCRIPTS, PATH_FLEXEXTRACT_DIR)
PATH_REL_FORTRAN_SRC = os.path.relpath(PATH_FORTRAN_SRC, PATH_FLEXEXTRACT_DIR)
