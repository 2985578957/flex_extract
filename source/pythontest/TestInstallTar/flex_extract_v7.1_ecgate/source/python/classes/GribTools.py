#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: July 2014
#
# @Change History:
#   February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - changed some naming
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Class Description:
#    The GRIB API provides all necessary tools to work directly with the
#    grib files. Nevertheless, the GRIB API tools are very basic and are in
#    direct connection with the grib files. This class provides some higher
#    functions which apply a set of GRIB API tools together in the respective
#    context. So, the class initially contains a list of grib files (their
#    names) and the using program then applies the methods directly on the
#    class objects without having to think about how the actual GRIB API
#    tools have to be arranged.
#
# @Class Content:
#    - __init__
#    - get_keys
#    - set_keys
#    - copy
#    - index
#
# @Class Attributes:
#    - filenames
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
from gribapi import grib_new_from_file, grib_is_defined, grib_get, \
                    grib_release, grib_set, grib_write, grib_index_read, \
                    grib_index_new_from_file, grib_index_add_file,  \
                    grib_index_write

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class GribTools(object):
    '''
    Class for GRIB utilities (new methods) based on GRIB API
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, filenames):
        '''
        @Description:
            Initialise an object of GribTools and assign a list
            of filenames.

        @Input:
            filenames: list of strings
                A list of filenames.

        @Return:
            <nothing>
        '''

        self.filenames = filenames

        return


    def get_keys(self, keynames, wherekeynames=[], wherekeyvalues=[]):
        '''
        @Description:
            get keyvalues for a given list of keynames
            a where statement can be given (list of key and list of values)

        @Input:
            keynames: list of strings
                List of keynames.

            wherekeynames: list of strings, optional
                Default value is an empty list.

            wherekeyvalues: list of strings, optional
                Default value is an empty list.

        @Return:
            return_list: list of strings
                List of keyvalues for given keynames.
        '''

        fileid = open(self.filenames, 'r')

        return_list = []

        while 1:
            gid_in = grib_new_from_file(fileid)

            if gid_in is None:
                break

            if len(wherekeynames) != len(wherekeyvalues):
                raise Exception("Number of key values and key names must be \
                                 the same. Give a value for each keyname!")

            select = True
            i = 0
            for wherekey in wherekeynames:
                if not grib_is_defined(gid_in, wherekey):
                    raise Exception("where key was not defined")

                select = (select and (str(wherekeyvalues[i]) ==
                                      str(grib_get(gid_in, wherekey))))
                i += 1

            if select:
                llist = []
                for key in keynames:
                    llist.extend([str(grib_get(gid_in, key))])
                return_list.append(llist)

            grib_release(gid_in)

        fileid.close()

        return return_list


    def set_keys(self, fromfile, keynames, keyvalues, wherekeynames=[],
                 wherekeyvalues=[], strict=False, filemode='w'):
        '''
        @Description:
            Opens the file to read the grib messages and then write
            them to a new output file. By default all messages are
            written out. Also, the keyvalues of the passed list of
            keynames are set or only those meeting the where statement.
            (list of key and list of values).

        @Input:
            fromfile: string
                Filename of the input file to read the grib messages from.

            keynames: list of strings
                List of keynames. Default is an empty list.

            keyvalues: list of strings
                List of keynames. Default is an empty list.

            wherekeynames: list of strings, optional
                Default value is an empty list.

            wherekeyvalues: list of strings, optional
                Default value is an empty list.

            strict: boolean, optional
                Decides if everything from keynames and keyvalues
                is written out the grib file (False) or only those
                meeting the where statement (True). Default is False.

            filemode: string, optional
                Sets the mode for the output file. Default is "w".

        @Return:
            <nothing>

        '''
        fout = open(self.filenames, filemode)
        fin = open(fromfile)

        while 1:
            gid_in = grib_new_from_file(fin)

            if gid_in is None:
                break

            if len(wherekeynames) != len(wherekeyvalues):
                raise Exception("Give a value for each keyname!")

            select = True
            i = 0
            for wherekey in wherekeynames:
                if not grib_is_defined(gid_in, wherekey):
                    raise Exception("where Key was not defined")

                select = (select and (str(wherekeyvalues[i]) ==
                                      str(grib_get(gid_in, wherekey))))
                i += 1

            if select:
                i = 0
                for key in keynames:
                    grib_set(gid_in, key, keyvalues[i])
                    i += 1

            grib_write(gid_in, fout)

            grib_release(gid_in)

        fin.close()
        fout.close()

        return

    def copy(self, filename_in, selectWhere=True,
             keynames=[], keyvalues=[], filemode='w'):
        '''
        Add the content of another input grib file to the objects file but
        only messages corresponding to keys/values passed to the function.
        The selectWhere switch decides if to copy the keys equal to (True) or
        different to (False) the keynames/keyvalues list passed to the function.

        @Input:
            filename_in: string
                Filename of the input file to read the grib messages from.

            selectWhere: boolean, optional
                Decides if to copy the keynames and values equal to (True) or
                different to (False) the keynames/keyvalues list passed to the
                function. Default is True.

            keynames: list of strings, optional
                List of keynames. Default is an empty list.

            keyvalues: list of strings, optional
                List of keynames. Default is an empty list.

            filemode: string, optional
                Sets the mode for the output file. Default is "w".

        @Return:
            <nothing>
        '''

        fin = open(filename_in)
        fout = open(self.filenames, filemode)

        while 1:
            gid_in = grib_new_from_file(fin)

            if gid_in is None:
                break

            if len(keynames) != len(keyvalues):
                raise Exception("Give a value for each keyname!")

            select = True
            i = 0
            for key in keynames:
                if not grib_is_defined(gid_in, key):
                    raise Exception("Key was not defined")

                if selectWhere:
                    select = (select and (str(keyvalues[i]) ==
                                          str(grib_get(gid_in, key))))
                else:
                    select = (select and (str(keyvalues[i]) !=
                                          str(grib_get(gid_in, key))))
                i += 1

            if select:
                grib_write(gid_in, fout)

            grib_release(gid_in)

        fin.close()
        fout.close()

        return

    def index(self, index_keys=["mars"], index_file="my.idx"):
        '''
        @Description:
            Create index file from a list of files if it does not exist or
            read an index file.

        @Input:
            index_keys: list of strings, optional
                Contains the list of key parameter names from
                which the index is to be created.
                Default is a list with a single entry string "mars".

            index_file: string, optional
                Filename where the indices are stored.
                Default is "my.idx".

        @Return:
            iid: integer
                Grib index id.
        '''
        print("... index will be done")
        iid = None

        if os.path.exists(index_file):
            iid = grib_index_read(index_file)
            print("Use existing index file: %s " % (index_file))
        else:
            for filename in self.filenames:
                print("Inputfile: %s " % (filename))
                if iid is None:
                    iid = grib_index_new_from_file(filename, index_keys)
                else:
                    grib_index_add_file(iid, filename)

            if iid is not None:
                grib_index_write(iid, index_file)

        print('... index done')

        return iid