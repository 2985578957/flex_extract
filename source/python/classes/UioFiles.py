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
import sys
import fnmatch

# software specific module from flex_extract
sys.path.append('../')
#import profiling
from mods.tools import silent_remove, get_list_as_string

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------

class UioFiles(object):
    '''Class to manipulate files. At initialisation it has the pattern
    which stores a regular expression pattern for the files, the path
    to the files and the files already.
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, path, pattern):
        '''Assignes a specific pattern for these files.

        Parameters
        ----------
        path : :obj:`string`
            Directory where to list the files.

        pattern : :obj:`string`
            Regular expression pattern. For example: '\*.grb'

        Return
        ------

        '''

        self.path = path
        self.pattern = pattern
        self.files = []

        self._list_files(self.path)

        return

    #@profiling.timefn
    def _list_files(self, path):
        '''Lists all files in the directory with the matching
        regular expression pattern.

        Parameters
        ----------
        path : :obj:`string`
            Path to the files.

        Return
        ------

        '''
        # Get the absolute path
        path = os.path.abspath(path)

        # get all files in the dir and subdir as absolut path
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, self.pattern):
                self.files.append(os.path.join(root, filename))

        return

    def __str__(self):
        '''Converts the list of files into a single string.
        The entries are sepereated by "," sign.

        Parameters
        ----------

        Return
        ------
        files_string : :obj:`string`
            The content of the list as a single string.
        '''

        filenames = [os.path.basename(f) for f in self.files]
        files_string = get_list_as_string(filenames, concatenate_sign=', ')

        return files_string

    def delete_files(self):
        '''Deletes the files.

        Parameters
        ----------

        Return
        ------

        '''

        for old_file in self.files:
            silent_remove(old_file)

        return
