#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
*******************************************************************************
 @Author: Anne Philipp (University of Vienna)

 @Date: August 2018

 @Change History:

 @License:
    (C) Copyright 2014-2020.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

 @Description:
    Contains constant value parameter for flex_extract.

*******************************************************************************
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys

sys.path.append('../Python')
import _config

# ------------------------------------------------------------------------------
# FILENAMES
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# DIRECTORY NAMES
# ------------------------------------------------------------------------------
TEST_DIR = 'Testing/Regression/Unit'
TESTFILES_DIR = 'Testfiles'
TESTINSTALL_DIR = 'InstallTar'
# ------------------------------------------------------------------------------
#  PATHES
# ------------------------------------------------------------------------------
PATH_TEST_DIR = os.path.join(_config.PATH_FLEXEXTRACT_DIR, TEST_DIR)
PATH_TESTFILES_DIR = os.path.join(PATH_TEST_DIR, TESTFILES_DIR)
PATH_TESTINSTALL_DIR = os.path.join(PATH_TEST_DIR, TESTINSTALL_DIR)
