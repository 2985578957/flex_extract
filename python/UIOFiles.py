#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - checken welche regelmässigen methoden auf diese Files noch angewendet werden
# und dann hier implementieren
# - add description of file!
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: October 2014

@ChangeHistory:
    November 2015 - Leopold Haimberger (University of Vienna):
        - modified method listFiles to work with glob instead of listdir
        - added pattern search in method listFiles

    February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - optimisation of method listFiles since it didn't work correctly
          for sub directories
        - additional speed up of method listFiles

@License:
    (C) Copyright 2014-2018.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    A standard python 2.6 or 2.7 installation

@Description:
    ...
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import glob
import fnmatch
import time
import profiling
# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class UIOFiles:
    '''
    Class to manipulate files. At initialisation it has the attribute
    suffix which stores a list of suffixes of the files associated
    with the instance of the class.
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, suffix):
        '''
        @Description:
            Assignes the suffixes of the files which should be
            associated with the instance of the class.

        @Input:
            self: instance of UIOFiles
                Description see class documentation.

            suffix: list of strings
                The types of files which should be manipulated such as
                ['grib', 'grb', 'grib1', 'grib2', 'grb1', 'grb2']

        @Return:
            <nothing>
        '''

        self.suffix = suffix

        return

    #@profiling.timefn
    def listFiles(self, path, pattern, callid=0):
        '''
        @Description:
            Lists all files in the directory with the matching
            regular expression pattern. The suffixes are already stored
            in a list attribute "suffix".

        @Input:
            self: instance of UIOFiles
                Description see class documentation.

            path: string
                Directory where to list the files.

            pattern: string
                Regular expression pattern. For example:
                '*OG_acc_SL*.'+c.ppid+'.*'

            callid: integer
                Id which tells the function if its the first call
                or a recursive call. Default and first call is 0.
                Everything different from 0 is ment to be a recursive case.

        @Return:
            <nothing>
        '''

        # initialize variable in first function call
        if callid == 0:
            self.files = []

        # Get the absolute path
        path = os.path.abspath(path)

        # get the file list of the path if its not a directory and
        # if it contains one of the suffixes
        self.files.extend([os.path.join(path, k) for k in os.listdir(path)
                           if fnmatch.fnmatch(k, pattern) and
                           os.path.splitext(k)[-1] in self.suffix])

        # find possible sub-directories in the path
        subdirs = [s for s in os.listdir(path)
                   if os.path.isdir(os.path.join(path, s))]

        # do recursive calls for sub-direcorties
        if subdirs:
            for subdir in subdirs:
                self.listFiles(os.path.join(path, subdir), pattern, callid=1)

        return
