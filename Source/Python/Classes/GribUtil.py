#!/usr/bin/env python3
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
#    - copy_dummy_msg
#    - index
#
# @Class Attributes:
#    - filenames
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class GribUtil(object):
    '''
    Class for GRIB utilities (new methods) based on GRIB API
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, filenames):
        '''Initialise an object of GribUtil and assign a list of filenames.

        Parameters
        ----------
        filenames : :obj:`list` of :obj:`strings`
             A list of filenames.

        Return
        ------

        '''

        self.filenames = filenames

        return


    def get_keys(self, keynames, wherekeynames=[], wherekeyvalues=[]):
        '''Get keyvalues for a given list of keynames a where statement
        can be given (list of key and list of values)

        Parameters
        ----------
        keynames : :obj:`list` of :obj:`string`
            List of keynames.

        wherekeynames : :obj:`list` of :obj:`string`, optional
            Default value is an empty list.

        wherekeyvalues : :obj:`list` of :obj:`string`, optional
            Default value is an empty list.

        Return
        ------
        return_list : :obj:`list` of :obj:`string`
            List of keyvalues for given keynames.
        '''
        from eccodes import (codes_new_from_file, codes_is_defined, codes_get,
                             codes_release)

        fileid = open(self.filenames, 'r')

        return_list = []

        while 1:
            gid = codes_new_from_file(fileid)

            if gid is None:
                break

            if len(wherekeynames) != len(wherekeyvalues):
                raise Exception("Number of key values and key names must be \
                                 the same. Give a value for each keyname!")

            select = True
            i = 0
            for wherekey in wherekeynames:
                if not codes_is_defined(gid, wherekey):
                    raise Exception("where key was not defined")

                select = (select and (str(wherekeyvalues[i]) ==
                                      str(codes_get(gid, wherekey))))
                i += 1

            if select:
                llist = []
                for key in keynames:
                    llist.extend([str(codes_get(gid, key))])
                return_list.append(llist)

            codes_release(gid)

        fileid.close()

        return return_list


    def set_keys(self, fromfile, keynames, keyvalues, wherekeynames=[],
                 wherekeyvalues=[], strict=False, filemode='w'):
        '''Opens the file to read the grib messages and then write
        the selected messages (with wherekeys) to a new output file.
        Also, the keyvalues of the passed list of keynames are set.

        Parameters
        ----------
        fromfile : :obj:`string`
            Filename of the input file to read the grib messages from.

        keynames : :obj:`list` of :obj:`string`
            List of keynames to set in the selected messages.
            Default is an empty list.

        keyvalues : :obj:`list` of :obj:`string`
            List of keyvalues to set in the selected messages.
            Default is an empty list.

        wherekeynames : :obj:`list` of :obj:`string`, optional
            List of keynames to select correct message.
            Default value is an empty list.

        wherekeyvalues : :obj:`list` of :obj:`string`, optional
            List of keyvalues for keynames to select correct message.
            Default value is an empty list.

        strict : :obj:`boolean`, optional
            Decides if everything from keynames and keyvalues
            is written out the grib file (False) or only those
            meeting the where statement (True). Default is False.

        filemode : :obj:`string`, optional
            Sets the mode for the output file. Default is "w".

        Return
        ------

        '''
        from eccodes import (codes_grib_new_from_file, codes_is_defined,
                             codes_get, codes_set, codes_write,
                             codes_set_values, codes_release)

        if len(wherekeynames) != len(wherekeyvalues):
            raise Exception("Give a value for each keyname!")

        fout = open(self.filenames, filemode)
        fin = open(fromfile)

        while 1:
            gid = codes_grib_new_from_file(fin)

            if gid is None:
                break

            select = True
            i = 0
            for wherekey in wherekeynames:
                if not codes_is_defined(gid, wherekey):
                    raise Exception("wherekey was not defined")

                select = (select and (str(wherekeyvalues[i]) ==
                                      str(codes_get(gid, wherekey))))
                i += 1

            if select:
                i = 0
                for key in keynames:
                    if key == 'values':
                        codes_set_values(gid, keyvalues[i])
                    else:
                        codes_set(gid, key, keyvalues[i])
                    i += 1

                codes_write(gid, fout)

            codes_release(gid)

        fin.close()
        fout.close()

        return

    def copy_dummy_msg(self, filename_in, selectWhere=True,
                 keynames=[], keyvalues=[], filemode='w'):
        '''Add the content of another input grib file to the objects file but
        only messages corresponding to keys/values passed to the function.
        The selectWhere switch decides if to copy the keys equal to (True) or
        different to (False) the keynames/keyvalues list passed to the function.

        Parameters
        ----------
        filename_in : :obj:`string`
            Filename of the input file to read the grib messages from.

        selectWhere : :obj:`boolean`, optional
            Decides if to copy the keynames and values equal to (True) or
            different to (False) the keynames/keyvalues list passed to the
            function. Default is True.

        keynames : :obj:`list` of :obj:`string`, optional
            List of keynames. Default is an empty list.

        keyvalues : :obj:`list` of :obj:`string`, optional
            List of keyvalues. Default is an empty list.

        filemode : :obj:`string`, optional
            Sets the mode for the output file. Default is "w".

        Return
        ------

        '''
        from eccodes import (codes_grib_new_from_file, codes_is_defined,
                             codes_get, codes_release, codes_write)

        if len(keynames) != len(keyvalues):
            raise Exception("Give a value for each keyname!")

        fin = open(filename_in, 'rb')
        fout = open(self.filenames, filemode)

        fields = 0

        while fields < 1:
            gid = codes_grib_new_from_file(fin)

            if gid is None:
                break

            select = True
            i = 0
            for key in keynames:
                if not codes_is_defined(gid, key):
                    raise Exception("Key was not defined")

                if selectWhere:
                    select = (select and (str(keyvalues[i]) ==
                                          str(codes_get(gid, key))))
                else:
                    select = (select and (str(keyvalues[i]) !=
                                          str(codes_get(gid, key))))
                i += 1

            if select:
                fields = fields + 1
                codes_write(gid, fout)

            codes_release(gid)

        fin.close()
        fout.close()

        return

    def index(self, index_keys=["mars"], index_file="my.idx"):
        '''Create index file from a list of files if it does not exist or
        read an index file.

        Parameters
        ----------
        index_keys: :obj:`list` of :obj:`string`, optional
            Contains the list of key parameter names from
            which the index is to be created.
            Default is a list with a single entry string "mars".

        index_file: :obj:`string`, optional
            Filename where the indices are stored.
            Default is "my.idx".

        Return
        ------
        iid: :obj:`integer`
            Grib index id.
        '''
        from eccodes import (codes_index_read, codes_index_new_from_file,
                             codes_index_add_file, codes_index_write)

        print("... index will be done")
        iid = None

        if os.path.exists(index_file):
            iid = codes_index_read(index_file)
            print("Use existing index file: %s " % (index_file))
        else:
            for filename in self.filenames:
                print("Inputfile: %s " % (filename))
                if iid is None:
                    iid = codes_index_new_from_file(filename, index_keys)
                else:
                    codes_index_add_file(iid, filename)

            if iid is not None:
                codes_index_write(iid, index_file)

        print('... index done')

        return iid
