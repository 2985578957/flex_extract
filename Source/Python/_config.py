#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Philipp (University of Vienna)
#
# @Date: August 2018
#
# @Change History:
#      June 2020 - Anne Philipp
#         - changed template filenames to .template
#
# @License:
#    (C) Copyright 2014-2020.
#    Anne Philipp, Leopold Haimberger
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#*******************************************************************************
'''Configurations for flex_extract.

Defines a couple of global constant parameters as well as filenames
and pathes.
'''
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import inspect
import platform

# ------------------------------------------------------------------------------
# PARAMETERS
# ------------------------------------------------------------------------------

_VERSION_STR = '7.1.2'

FLAG_ON_ECMWFSERVER = 'ecgb' in platform.node()

QUEUES_LIST = ['ecgate', 'cca', 'ccb']

INSTALL_TARGETS = ['local', 'ecgate', 'cca', 'ccb']

CDS_DATASET_ML = 'reanalysis-era5-complete'
CDS_DATASET_SFC = 'reanalysis-era5-single-levels'

# up-to-date available maximum level numbers at ECMWF, 05.10.2018
MAX_LEVEL_LIST = [16, 19, 31, 40, 50, 60, 62, 91, 137]

# ------------------------------------------------------------------------------
# FILENAMES
# ------------------------------------------------------------------------------

FILE_MARS_REQUESTS = 'mars_requests.csv'
FORTRAN_EXECUTABLE = 'calc_etadot'
TEMPFILE_USER_ENVVARS = 'ECMWF_ENV.template'
FILE_USER_ENVVARS = 'ECMWF_ENV'
TEMPFILE_INSTALL_COMPILEJOB = 'installscript.template'
FILE_INSTALL_COMPILEJOB = 'compilejob.ksh'
TEMPFILE_INSTALL_JOB = 'jobscript.template'
TEMPFILE_JOB = 'submitscript.template'
FILE_JOB_OD = 'job.ksh'
FILE_JOB_OP = 'jopoper.ksh'
TEMPFILE_NAMELIST = 'calc_etadot_nml.template'
FILE_NAMELIST = 'fort.4'
FILE_GRIB_INDEX = 'date_time_stepRange.idx'
FILE_GRIBTABLE = 'ecmwf_grib1_table_128'

# ------------------------------------------------------------------------------
# DIRECTORY NAMES
# ------------------------------------------------------------------------------

FLEXEXTRACT_DIRNAME = 'flex_extract_v' + _VERSION_STR
INPUT_DIRNAME_DEFAULT = 'Workspace'

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
PATH_RUN_DIR = os.path.join(PATH_FLEXEXTRACT_DIR, 'Run')
PATH_SOURCES = os.path.join(PATH_FLEXEXTRACT_DIR, 'Source')
PATH_TEMPLATES = os.path.join(PATH_FLEXEXTRACT_DIR, 'Templates')
PATH_ECMWF_ENV = os.path.join(PATH_RUN_DIR, FILE_USER_ENVVARS)
PATH_GRIBTABLE = os.path.join(PATH_TEMPLATES, FILE_GRIBTABLE)
PATH_JOBSCRIPTS = os.path.join(PATH_RUN_DIR, 'Jobscripts')
PATH_FORTRAN_SRC = os.path.join(PATH_SOURCES, 'Fortran')
PATH_PYTHONTEST_SRC = os.path.join(PATH_SOURCES, 'Pythontest')
PATH_INPUT_DIR = os.path.join(PATH_RUN_DIR, INPUT_DIRNAME_DEFAULT)
PATH_TEST = os.path.join(PATH_FLEXEXTRACT_DIR, 'Testing')
if os.getenv('CONTROL'):
    # this is only needed if (gateway) version with job script is used!
    # because job is directly submitted from SCRATCH and because the
    # CONTROL file is stored there, the normal path is not valid.
    PATH_CONTROLFILES = '.'
else:
    PATH_CONTROLFILES = os.path.join(PATH_RUN_DIR, 'Control')
#
# ------------------------------------------------------------------------------
# RELATIVE PATHES FOR INSTALLATION TAR-BALL
# ------------------------------------------------------------------------------

PATH_REL_PYTHON_SRC = os.path.relpath(PATH_LOCAL_PYTHON, PATH_FLEXEXTRACT_DIR)
PATH_REL_PYTHONTEST_SRC = os.path.relpath(PATH_PYTHONTEST_SRC, PATH_FLEXEXTRACT_DIR)
PATH_REL_CONTROLFILES = os.path.relpath(PATH_CONTROLFILES, PATH_FLEXEXTRACT_DIR)
PATH_REL_TEMPLATES = os.path.relpath(PATH_TEMPLATES, PATH_FLEXEXTRACT_DIR)
PATH_REL_ECMWF_ENV = os.path.relpath(PATH_ECMWF_ENV, PATH_FLEXEXTRACT_DIR)
PATH_REL_RUN_DIR = os.path.relpath(PATH_RUN_DIR, PATH_FLEXEXTRACT_DIR)
PATH_REL_JOBSCRIPTS = os.path.relpath(PATH_JOBSCRIPTS, PATH_FLEXEXTRACT_DIR)
PATH_REL_FORTRAN_SRC = os.path.relpath(PATH_FORTRAN_SRC, PATH_FLEXEXTRACT_DIR)
PATH_REL_TEST = os.path.relpath(PATH_TEST, PATH_FLEXEXTRACT_DIR)
