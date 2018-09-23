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
#    - __str__
#    - __list_files__
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
from mods.tools import silent_remove, get_list_as_string

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------

class UioFiles(object):
    '''
    Class to manipulate files. At initialisation it has the pattern
    which stores a regular expression pattern for the files, the path
    to the files and the files already.
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, path, pattern):
        '''
        @Description:
            Assignes a specific pattern for these files.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

            path: string
                Directory where to list the files.

            pattern: string
                Regular expression pattern. For example: '*.grb'

        @Return:
            <nothing>
        '''

        self.path = path
        self.pattern = pattern
        self.files = []

        self.__list_files__(self.path)

        return

    #@profiling.timefn
    def __list_files__(self, path):
        '''
        @Description:
            Lists all files in the directory with the matching
            regular expression pattern.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

            path: string
                Path to the files.

        @Return:
            <nothing>
        '''
        # Get the absolute path
        path = os.path.abspath(path)

        # get all files in the dir and subdir as absolut path
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, self.pattern):
                self.files.append(os.path.join(root, filename))

        return

    def __str__(self):
        '''
        @Description:
            Converts the list of files into a single string.
            The entries are sepereated by "," sign.

        @Input:
            self: instance of UioFiles
                Description see class documentation.

        @Return:
            files_string: string
                The content of the list as a single string.
        '''

        filenames = [os.path.basename(f) for f in self.files]
        files_string = get_list_as_string(filenames, concatenate_sign=', ')

        return files_string

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
