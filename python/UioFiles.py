#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - modified method list_files to work with glob instead of listdir
#        - added pattern search in method list_files
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - optimisation of method list_files since it didn't work correctly
#          for sub directories
#        - additional speed up of method list_files
#        - modified the class so that it is initiated with a pattern instead
#          of suffixes. Gives more precision in selection of files.
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Class Decription:
#    The class is for file manipulation. It is initiated with a regular
#    expression pattern for this instance and can produce a list of Files
#    from the given file pattern. These files can be deleted.
#
# @Class Content:
#    - __init__
#    - list_files
#    - delete_files
#
# @Class Attributes:
#    - pattern
#    - files
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import fnmatch

# software specific module from flex_extract
#import profiling
from tools import silent_remove

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------

class UioFiles(object):
    '''
    Class to manipulate files. At initialisation it has the attribute
    pattern which stores a regular expression pattern for the files associated
    with the instance of the class.
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, pattern):
        '''
        @Description:
            Assignes a specific pattern for these files.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

            pattern: string
                Regular expression pattern. For example: '*.grb'

        @Return:
            <nothing>
        '''

        self.pattern = pattern
        self.files = None

        return

    #@profiling.timefn
    def list_files(self, path, callid=0):
        '''
        @Description:
            Lists all files in the directory with the matching
            regular expression pattern.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

            path: string
                Directory where to list the files.

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
        # if it contains the pattern
        self.files.extend([os.path.join(path, k) for k in os.listdir(path)
                           if fnmatch.fnmatch(k, self.pattern)])

        # find possible sub-directories in the path
        subdirs = [s for s in os.listdir(path)
                   if os.path.isdir(os.path.join(path, s))]

        # do recursive calls for sub-direcorties
        if subdirs:
            for subdir in subdirs:
                self.list_files(os.path.join(path, subdir), callid=1)

        return

    def delete_files(self):
        '''
        @Description:
            Deletes the files.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

        @Return:
            <nothing>
        '''

        for old_file in self.files:
            silent_remove(old_file)

        return
