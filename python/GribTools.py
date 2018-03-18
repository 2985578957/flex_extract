#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - GribTools name möglicherweise etwas verwirrend.
# - change self.filename in self.filenames!!!
# -
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: July 2014

@ChangeHistory:
   February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - changed some naming

@License:
    (C) Copyright 2014 UIO.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    - A standard python 2.6 or 2.7 installation
    - dateutils
    - matplotlib (optional, for debugging)
    - ECMWF specific packages, all available from https://software.ecmwf.int/
        ECMWF WebMARS, gribAPI with python enabled, emoslib and
        ecaccess web toolkit

@Description:
    Further documentation may be obtained from www.flexpart.eu.

    Functionality provided:
        Prepare input 3D-wind fields in hybrid coordinates +
        surface fields for FLEXPART runs
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from gribapi import *
import traceback
import sys, os

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class GribTools:
    '''
    Class for GRIB utilities (new methods) based on GRIB API
    '''
    # --------------------------------------------------------------------------
    # FUNCTIONS
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

        self.filename = filenames

        return


    def getkeys(self, keynames, wherekeynames=[], wherekeyvalues=[]):
        '''
        @Description:
            get keyvalues for a given list of keynames
            a where statement can be given (list of key and list of values)

        @Input:
            keynames: list of strings
                List of keynames.

            wherekeynames: list of ???, optional
                Default value is an empty list.

            wherekeyvalues: list of ???, optional
                Default value is an empty list.

        @Return:
            return_list: list of strings
                List of keyvalues for given keynames.
        '''

        fileid = open(self.filename, 'r')

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


    def setkeys(self, fromfile, keynames, keyvalues, wherekeynames=[],
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

            keynames: list of ???
                List of keynames. Default is an empty list.

            keyvalues: list of ???
                List of keynames. Default is an empty list.

            wherekeynames: list of ???, optional
                Default value is an empty list.

            wherekeyvalues: list of ???, optional
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
        fout = open(self.filename, filemode)
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

#AP is it secured that the order of keynames is equal to keyvalues?
            if select:
                i = 0
                for key in keynames:
                    grib_set(gid_in, key, keyvalues[i])
                    i += 1

#AP this is a redundant code section
# delete the if/else :
#
#           grib_write(gid_in, fout)
#
            if strict:
                if select:
                    grib_write(gid_in, fout)
            else:
                grib_write(gid_in, fout)
#AP end
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

            keynames: list of ???, optional
                List of keynames. Default is an empty list.

            keyvalues: list of ???, optional
                List of keynames. Default is an empty list.

            filemode: string, optional
                Sets the mode for the output file. Default is "w".

        @Return:
            <nothing>
        '''

        fin = open(filename_in)
        fout = open(self.filename, filemode)

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
        self.iid = None

        if (os.path.exists(index_file)):
            self.iid = grib_index_read(index_file)
            print("Use existing index file: %s " % (index_file))
        else:
            for file in self.filename:
                print("Inputfile: %s " % (file))
                if self.iid is None:
                    self.iid = grib_index_new_from_file(file, index_keys)
                else:
                    grib_index_add_file(self.iid, file)

            if self.iid is not None:
                grib_index_write(self.iid, index_file)

        print('... index done')

        return self.iid





