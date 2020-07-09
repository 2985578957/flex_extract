#!/usr/bin/env python3
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
#    February - December 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - optimisation of method list_files since it didn't work correctly
#          for sub directories
#        - additional speed up of method list_files
#        - modified the class so that it is initiated with a pattern instead
#          of suffixes. Gives more precision in selection of files.
#        - added delete method
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

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import fnmatch

# software specific modules from flex_extract
#pylint: disable=wrong-import-position
sys.path.append('../')
from Mods.tools import silent_remove, get_list_as_string
#pylint: enable=wrong-import-position

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------

class UioFiles(object):
    """Collection of files matching a specific pattern.

    The pattern can contain regular expressions for the files.
    The files are listed and can be transformed to a single string or
    they can be deleted.

    Attributes
    ----------
    path : str
        Directory where to list the files.

    pattern : str
        Regular expression pattern. For example: '*.grb'

    files : list of str
        List of files matching the pattern in the path.
    """
    # --------------------------------------------------------------------------
    # CLASS METHODS
    # --------------------------------------------------------------------------
    def __init__(self, path, pattern):
        """Assignes a specific pattern for these files.

        Parameters
        ----------
        path : str
            Directory where to list the files.

        pattern : str
            Regular expression pattern. For example: '*.grb'

        Return
        ------

        """

        self.path = path
        self.pattern = pattern
        self.files = []

        self._list_files(self.path)

        return


    def _list_files(self, path):
        """Lists all files in the directory with the matching
        regular expression pattern.

        Parameters
        ----------
        path : str
            Path to the files.

        Return
        ------

        """
        # Get the absolute path
        path = os.path.abspath(path)

        # get all files in the dir and subdir as absolut path
        # pylint: disable=W0612
        for root, dirnames, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, self.pattern):
                self.files.append(os.path.join(root, filename))

        return


    def __str__(self):
        """Converts the list of files into a single string.
        The entries are sepereated by "," sign.

        Parameters
        ----------

        Return
        ------
        files_string : str
            The content of the list as a single string.
        """

        filenames = [os.path.basename(f) for f in self.files]
        files_string = get_list_as_string(filenames, concatenate_sign=', ')

        return files_string


    def delete_files(self):
        """Deletes the files.

        Parameters
        ----------

        Return
        ------

        """

        for old_file in self.files:
            silent_remove(old_file)

        return
