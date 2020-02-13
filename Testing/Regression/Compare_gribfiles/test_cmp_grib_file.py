#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comparison of resulting Grib files of two flex_extract versions.



The script should be called like:

    python test_cmp_grib_files.py -r <path-to-reference-files> -n <path-to-new-files>  -p <file-pattern>

Note
----

Licence:
--------
    (C) Copyright 2014-2019.

    SPDX-License-Identifier: CC-BY-4.0

    This work is licensed under the Creative Commons Attribution 4.0
    International License. To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/ or send a letter to
    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.


Example
-------
    python test_cmp_grib_file.py -r 7.0.4/EA5/ -n 7.1/EA5/ -p 'EA*'
"""

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
from datetime import datetime
from eccodes import GribFile, GribMessage

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def get_cmdline_params(parlist, debug=True):

    import getopt

    iref_path = '' # e.g. Reference_files
    inew_path = '' # e.g. New_files
    smatch = '' # e.g. files matching pattern

    try:
        opts, pars = getopt.getopt(parlist,
                                   "hr:n:p:",
                                   ["ipref=", "ipnew=", "pattern="])
    except getopt.GetoptError:
        print('test_cmp_grib_file.py -r <ipref> -n <ipnew> -p <pattern>')
        sys.exit(2)

    for opt, par in opts:
        if opt == '-h':
            print('test_cmp_grib_file.py -r <ipref> -n <ipnew> -p <pattern>')
            sys.exit()
        elif opt in ("-r", "--ipref"):
            iref_path = par
        elif opt in ("-n", "--ipnew"):
            inew_path = par
        elif opt in ("-p", "--pattern"):
            smatch = par

    if iref_path == '':
        sys.exit('NO REFERENCE INPUT PATH SET!')
    if inew_path == '':
        sys.exit('NO "NEW" COMPARISON INPUT PATH SET!')
    if smatch == '':
        sys.exit('NO MATCHING PATTERN FOR FILES SET!')

    if debug:
        print("\n\nWelcome!")
        print('Reference path is: ', iref_path)
        print('New path is: ', inew_path)
        print('Filepattern is: ', smatch)

    return iref_path, inew_path, smatch

def get_files(ipath, matchingstring, debug=True):
    """
        @Description:
            Get filenames from input path matching the
            string or regular expression and return it.

        @Input:
            ipath: string
                Path to the files.

            matchingstring: string
                A string defining the filenames,
                with or without regular exprssion.

        @Return
            filename: list of strings
                A list of all files matching the pattern of
                matchingstring.
    """
    import fnmatch

    files = []

    for fn in os.listdir(ipath):
        if fnmatch.fnmatch(fn, matchingstring):
            files.append(fn)

    filelist = sorted(files)
    if debug:
        print('The input files are: %s' %(filelist))

    return filelist

def cmp_files_list(flist1, flist2):
    '''
    '''

    # 1. same length?
    length = len(flist1) == len(flist2)
    if not length:
        print('There are not the same amount of files.')
        sys.exit('Message 1')

    # 2. same content?
    content = [True for i, j in zip(flist1, flist2) if i == j]
    if not len(content) == len(flist1):
        print('Not the same file list')
        sys.exit('Message 2')

    return True


def cmp_number_messages(iref, flist1, inew, flist2):

    ref_dict = {}
    new_dict = {}
    res_dict = {}
    for file in flist1:
        with GribFile(os.path.join(iref,file)) as grib:
            ref_dict[file] = len(grib)
        with GribFile(os.path.join(inew,file)) as grib:
            new_dict[file] = len(grib)

        res_dict[file] = ref_dict[file] == new_dict[file]

    for k, res in res_dict.items():
        if not res == True:
            print('LOG: Amount of messages in files {} are not the same!'.format(k))

    return True


def cmp_grib_msg_header(ipath_ref, ipath_new, filelist):
    from subprocess import Popen, PIPE
    # ref_dict = {}
    # new_dict = {}
    # for file in flist1:
        # with GribFile(os.path.join(iref,file)) as grib:
            # for i in range(len(grib)):
                # msg = GribMessage(grib)
                # ref_dict[file] = {}
                # ref_dict[file][i] = [msg['shortName'],msg['level'],
                                  # msg['editionNumber'],msg['dataDate'],
                                  # msg['dataTime'],msg['marsClass'],
                                  # msg['type'], msg['gridType'],
                                  # msg['stepRange']]
    error_flag = False
    cmp_flag = False
    for file in filelist:
        try:
            res = Popen(['grib_compare', '-H',
                         ipath_ref + '/' + file,
                         ipath_new + '/' + file],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, error = res.communicate()#.decode("utf-8"))
            if error:
                print('... ERROR: \n\t{}'.format(error.decode()))
                error_flag = True
            if output:
                print('{}'.format(output.decode()))
                cmp_flag = True
        except ValueError as e:
            print('... ERROR CODE: ' + str(e.returncode))
            print('... ERROR MESSAGE:\n \t ' + str(res))
            error_flag = True
        except OSError as e:
            print('... ERROR CODE: ' + str(e.errno))
            print('... ERROR MESSAGE:\n \t ' + str(e.strerror))
            error_flag = True

    if error_flag:
        sys.exit('... ERROR IN GRIB MESSAGE COMPARISON!')
    if cmp_flag:
        sys.exit('... FILES HAVE DIFFERENCES IN GRIB MESSAGES!')

    return True


def cmp_grib_msg_statistics(ipath_ref, ipath_new, filelist):

    from subprocess import Popen, PIPE

    error_flag = False
    cmp_flag = False
    for file in filelist:
        try:
            res = Popen(['grib_compare', '-c', 'statistics:n',
                         ipath_ref + '/' + file,
                         ipath_new + '/' + file],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, error = res.communicate()#.decode("utf-8"))
            if error:
                print('... ERROR: \n\t{}'.format(error.decode()))
                error_flag = True
            if output:
                print('\nIn File: {}'.format(file))
                print('{}'.format(output.decode()))
                cmp_flag = True
        except ValueError as e:
            print('... ERROR CODE: ' + str(e.returncode))
            print('... ERROR MESSAGE:\n \t ' + str(res))
            error_flag = True
        except OSError as e:
            print('... ERROR CODE: ' + str(e.errno))
            print('... ERROR MESSAGE:\n \t ' + str(e.strerror))
            error_flag = True

    if error_flag:
        sys.exit('... ERROR IN GRIB MESSAGE COMPARISON!')
    if cmp_flag:
        sys.exit('... FILES HAVE DIFFERENT STATISTICS!')
    return True

if __name__ == '__main__':

    # get the parameter list of program call
    ref_path, new_path, fmatch = get_cmdline_params(sys.argv[1:])

    # get the list of files of both cases
    ref_files = get_files(ref_path, fmatch)
    new_files = get_files(new_path, fmatch)

    # flag to store successfull tests
    suc = True

    # 1. Does the 2 cases contain the same list of files?
    suc = True if suc and cmp_files_list(ref_files, new_files) else False

    # 2. Does each file in both cases contain the same amount of messages?
    suc = True if suc and cmp_number_messages(ref_path, ref_files, new_path, new_files) else False

    # 3. Does each file has the same parameters (in Header)?
    # Since we can be sure that both cases have the same files,
    # we just use 1 filelist
    suc = True if suc and cmp_grib_msg_header(ref_path, new_path, new_files) else False

    # 4. Are the statistics of each message the same?
    # Since we can be sure that both cases have the same files,
    # we just use 1 filelist
    suc = True if suc and cmp_grib_msg_statistics(ref_path, new_path, new_files) else False

    # If the program comes this far and flag "suc" = True,
    # all tests were successful
    if suc:
        exit('GRIB_COMPARISON: SUCCESSFULL!')
    else:
        exit('GRIB_COMPARISON: FAILURE!')
