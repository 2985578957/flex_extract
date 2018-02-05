#************************************************************************
# TODO AP
#
# - File name und Klassenname gleichsetzen?
# - checken welche regelmässigen methoden auf diese Files noch angewendet werden
# und dann hier implementieren
# - löschen?
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: October 2014

@ChangeHistory:
   Anne Philipp - February 2018:
       Added documentation and applied pep8 style guides

@License:
    (C) Copyright 2014 UIO.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
"""


# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import glob

# ------------------------------------------------------------------------------
# Class
# ------------------------------------------------------------------------------
class UIOFiles:
    '''
    Class to manipulate files. At initialisation it has the attribute
    suffix which stores a list of suffixes of the files associated
    with the instance of the class.
    '''
    # --------------------------------------------------------------------------
    # FUNCTIONS
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
                Types of files to manipulate such as
                ['.grib', 'grb', 'grib1', 'grib2', 'grb1','grb2']

        @Return:
            <nothing>
        '''
        self.suffix = suffix
        return

    def listFiles(self, pathname, pattern):
        '''
        @Description:
            Lists all files in the directory with the matching
            regular expression pattern. The suffixes are already stored
            in a list attribute "suffix".

        @Input:
            self: instance of UIOFiles
                Description see class documentation.

            pathname: string
                Directory where to list the files.

            pattern: string
                Regular expression pattern. For example:
                '*OG_acc_SL*.'+c.ppid+'.*'

        @Return:
            <nothing>
        '''
        # Get the absolute path of the pathname parameter
        pathname = os.path.abspath(pathname)

        # Get a list of files in pathname
        filesInCurDir0 = glob.glob(pathname + '/' + pattern)
        filesInCurDir = []
        for f in filesInCurDir0:
            filesInCurDir.append(f.split('/')[-1])
        self.counter = 0
        self.files = []
        # Traverse through all files
        for file in filesInCurDir:
            curFile = os.path.join(pathname, file)

            # Check if it's a normal file or directory
            if os.path.isfile(curFile):
                # Get the file extension
                fileNoExt, curFileExtension = os.path.splitext(curFile)
                # Check if the file has an extension of typical video files
                if curFileExtension in self.suffix:
                    # We have got a file file! Increment the counter
                    self.counter += 1
                    # add this filename in the list
                    self.files.append(curFile)
            else:
                # We got a directory, enter into it for further processing
                self.listFiles(curFile)

        return