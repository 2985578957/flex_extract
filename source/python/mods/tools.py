#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Philipp (University of Vienna)
#
# @Date: May 2018
#
# @Change History:
#    October 2014 - Anne Fouilloux (University of Oslo)
#        - created functions silent_remove and product (taken from ECMWF)
#
#    November 2015 - Leopold Haimberger (University of Vienna)
#        - created functions: interpret_args_and_control, clean_up
#          my_error, normal_exit, init128, to_param_id
#
#    April 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - moved all functions from file Flexparttools to this file tools
#        - added function get_list_as_string
#        - seperated args and control interpretation
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Modul Description:
#    This module contains a couple of helpful functions which are
#    used in different places in flex_extract.
#
# @Module Content:
#    - get_cmdline_args
#    - clean_up
#    - my_error
#    - normal_exit
#    - product
#    - silent_remove
#    - init128
#    - to_param_id
#    - get_list_as_string
#    - make_dir
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import errno
import sys
import glob
import subprocess
import traceback
import exceptions
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

def none_or_str(value):
    '''Converts the input string into pythons None-type if the string
    contains string "None".

    Parameters
    ----------
    value : :obj:`string`
        String to be checked for the "None" word.

    Return
    ------
    None or value:
        Return depends on the content of the input value. If it was "None",
        then the python type None is returned. Otherwise the string itself.
    '''
    if value == 'None':
        return None
    return value

def none_or_int(value):
    '''Converts the input string into pythons None-type if the string
    contains string "None". Otherwise it is converted to an integer value.

    Parameters
    ----------
    value : :obj:`string`
        String to be checked for the "None" word.

    Return
    ------
    None or int(value):
        Return depends on the content of the input value. If it was "None",
        then the python type None is returned. Otherwise the string is
        converted into an integer value.
    '''
    if value == 'None':
        return None
    return int(value)

def get_cmdline_args():
    '''Decomposes the command line arguments and assigns them to variables.
    Apply default values for non mentioned arguments.

    Parameters
    ----------

    Return
    ------
    args : :obj:`Namespace`
        Contains the commandline arguments from script/program call.
    '''

    parser = ArgumentParser(description='Retrieve FLEXPART input from \
                                ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # control parameters that override control file values
    parser.add_argument("--start_date", dest="start_date",
                        type=none_or_str, default=None,
                        help="start date YYYYMMDD")
    parser.add_argument("--end_date", dest="end_date",
                        type=none_or_str, default=None,
                        help="end_date YYYYMMDD")
    parser.add_argument("--date_chunk", dest="date_chunk",
                        type=none_or_int, default=None,
                        help="# of days to be retrieved at once")
    parser.add_argument("--controlfile", dest="controlfile",
                        type=none_or_str, default='CONTROL.temp',
                        help="file with CONTROL parameters")
    parser.add_argument("--basetime", dest="basetime",
                        type=none_or_int, default=None,
                        help="base such as 00 or 12 (for half day retrievals)")
    parser.add_argument("--step", dest="step",
                        type=none_or_str, default=None,
                        help="steps such as 00/to/48")
    parser.add_argument("--levelist", dest="levelist",
                        type=none_or_str, default=None,
                        help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area",
                        type=none_or_str, default=None,
                        help="area defined as north/west/south/east")

    # some switches
    parser.add_argument("--debug", dest="debug",
                        type=none_or_int, default=None,
                        help="debug mode - leave temporary files intact")
    parser.add_argument("--request", dest="request",
                        type=none_or_int, default=None,
                        help="list all mars requests in file mars_requests.dat")
    parser.add_argument("--public", dest="public",
                        type=none_or_int, default=None,
                        help="public mode - retrieves the public datasets")
    parser.add_argument("--rrint", dest="rrint",
                        type=none_or_int, default=None,
                        help="select old or new precipitation interpolation \
                        0 - old method\
                        1 - new method (additional subgrid points)")

    # set directories
    parser.add_argument("--inputdir", dest="inputdir",
                        type=none_or_str, default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir",
                        type=none_or_str, default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpartdir", dest="flexpartdir",
                        type=none_or_str, default=None,
                        help="FLEXPART root directory (to find grib2flexpart \
                        and COMMAND file)\n Normally flex_extract resides in \
                        the scripts directory of the FLEXPART distribution")

    # this is only used by prepare_flexpart.py to rerun a postprocessing step
    parser.add_argument("--ppid", dest="ppid",
                        type=none_or_str, default=None,
                        help="specify parent process id for \
                        rerun of prepare_flexpart")

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        type=none_or_str, default="job.temp",
                        help="job template file for submission to ECMWF")
    parser.add_argument("--queue", dest="queue",
                        type=none_or_str, default=None,
                        help="queue for submission to ECMWF \
                        (e.g. ecgate or cca )")

    args = parser.parse_args()

    return args

def read_ecenv(filepath):
    '''Reads the file into a dictionary where the key values are the parameter
    names.

    Parameters
    ----------
    filepath : :obj:`string`
        Path to file where the ECMWF environment parameters are stored.

    Return
    ------
    envs : :obj:`dictionary`
        Contains the environment parameter ecuid, ecgid, gateway
        and destination for ECMWF server environments.
    '''
    envs= {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                data = line.strip().split()
                envs[str(data[0])] = str(data[1])
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... Error occured while trying to read ECMWF_ENV '
                     'file: ' + str(filepath))

    return envs

def clean_up(c):
    '''Remove files from the intermediate directory (inputdir).

    It keeps the final FLEXPART input files if program runs without
    ECMWF Api and keywords "ectrans" or "ecstorage" are set to "1".

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''

    print("... clean inputdir!")

    cleanlist = glob.glob(os.path.join(c.inputdir, "*"))

    if cleanlist:
        for element in cleanlist:
            if c.prefix not in element:
                silent_remove(element)
            if c.ecapi is False and (c.ectrans == 1 or c.ecstorage == 1):
                silent_remove(element)
        print("... done!")
    else:
        print("... nothing to clean!")

    return


def my_error(users, message='ERROR'):
    '''Prints a specified error message which can be passed to the function
    before exiting the program.

    Parameters
    ----------
    user : :obj:`list` of :obj:`string`
        Contains all email addresses which should be notified.
        It might also contain just the ecmwf user name which wil trigger
        mailing to the associated email address for this user.

    message : :obj:`string`, optional
        Error message. Default value is "ERROR".

    Return
    ------

    '''

    trace = '\n'.join(traceback.format_stack())
    full_message = message + '\n\n' + trace

    print(full_message)

    send_mail(users, 'ERROR', full_message)

    sys.exit(1)

    return


def send_mail(users, success_mode, message):
    '''Prints a specific exit message which can be passed to the function.

    Parameters
    ----------
    users : :obj:`list` of :obj:`string`
        Contains all email addresses which should be notified.
        It might also contain just the ecmwf user name which wil trigger
        mailing to the associated email address for this user.

    success_mode : :obj:``string`
        States the exit mode of the program to put into
        the mail subject line.

    message : :obj:`string`, optional
        Message for exiting program. Default value is "Done!".

    Return
    ------

    '''

    for user in users:
        if '${USER}' in user:
            user = os.getenv('USER')
        try:
            p = subprocess.Popen(['mail', '-s flex_extract_v7.1 ' +
                                  success_mode, os.path.expandvars(user)],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 bufsize=1)
            pout = p.communicate(input=message + '\n\n')[0]
        except ValueError as e:
            print('... ERROR: ' + str(e))
            sys.exit('... Email could not be sent!')
        except OSError as e:
            print('... ERROR CODE: ' + str(e.errno))
            print('... ERROR MESSAGE:\n \t ' + str(e.strerror))
            sys.exit('... Email could not be sent!')
        else:
            print('Email sent to ' + os.path.expandvars(user))

    return


def normal_exit(message='Done!'):
    '''Prints a specific exit message which can be passed to the function.

    Parameters
    ----------
    message : :obj:`string`, optional
        Message for exiting program. Default value is "Done!".

    Return
    ------

    '''

    print(str(message))

    return


def product(*args, **kwds):
    '''Creates combinations of all passed arguments.

    This method combines the single characters of the passed arguments
    with each other. So that each character of each argument value
    will be combined with each character of the other arguments as a tuple.

    Note
    ----
    This method is taken from an example at the ECMWF wiki website.
    https://software.ecmwf.int/wiki/display/GRIB/index.py; 2018-03-16

    Example
    -------
    product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy

    product(range(2), repeat = 3) --> 000 001 010 011 100 101 110 111

    Parameters
    ----------
    \*args : :obj:`list` or :obj:`string`
        Positional arguments (arbitrary number).

    \*\*kwds : :obj:`dictionary`
        Contains all the keyword arguments from \*args.

    Return
    ------
    prod : :obj:`tuple`
        Return will be done with "yield". A tuple of combined arguments.
        See example in description above.
    '''
    try:
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x + [y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)
    except TypeError as e:
        sys.exit('... PRODUCT GENERATION FAILED!')

    return


def silent_remove(filename):
    '''Remove file if it exists.
    The function does not fail if the file does not exist.

    Parameters
    ----------
    filename : :obj:`string`
        The name of the file to be removed without notification.

    Return
    ------

    '''
    try:
        os.remove(filename)
    except OSError as e:
        # errno.ENOENT  =  no such file or directory
        if e.errno == errno.ENOENT:
            pass
        else:
            raise  # re-raise exception if a different error occured

    return


def init128(filepath):
    '''Opens and reads the grib file with table 128 information.

    Parameters
    ----------
    filepath : :obj:`string`
        Path to file of ECMWF grib table number 128.

    Return
    ------
    table128 : :obj:`dictionary`
        Contains the ECMWF grib table 128 information.
        The key is the parameter number and the value is the
        short name of the parameter.
    '''
    table128 = dict()
    try:
        with open(filepath) as f:
            fdata = f.read().split('\n')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... Error occured while trying to read parameter '
                 'table file: ' + str(filepath))
    else:
        for data in fdata:
            if data[0] != '!':
                table128[data[0:3]] = data[59:64].strip()

    return table128


def to_param_id(pars, table):
    '''Transform parameter names to parameter ids with ECMWF grib table 128.

    Parameters
    ----------
    pars : :obj:`string`
        Addpar argument from CONTROL file in the format of
        parameter names instead of ids. The parameter short
        names are sepearted with "/" and they are passed as
        one single string.

    table : :obj:`dictionary`
        Contains the ECMWF grib table 128 information.
        The key is the parameter number and the value is the
        short name of the parameter.

    Return
    ------
    ipar : :obj:`list` of :obj:`integer`
        List of addpar parameters from CONTROL file transformed to
        parameter ids in the format of integer.
    '''
    if not pars:
        return []
    if not isinstance(pars, str):
        pars=str(pars)

    cpar = pars.upper().split('/')
    ipar = []
    for par in cpar:
        for k, v in table.iteritems():
            if par == k or par == v:
                ipar.append(int(k))
                break
        else:
            print('Warning: par ' + par + ' not found in table 128')

    return ipar

def get_list_as_string(list_obj, concatenate_sign=', '):
    '''Converts a list of arbitrary content into a single string.

    Parameters
    ----------
    list_obj : :obj:`list`
        A list with arbitrary content.

    concatenate_sign : :obj:`string`, optional
        A string which is used to concatenate the single
        list elements. Default value is ", ".

    Return
    ------
    str_of_list : :obj:`string`
        The content of the list as a single string.
    '''

    if not isinstance(list_obj, list):
        list_obj = list(list_obj)
    str_of_list = concatenate_sign.join(str(l) for l in list_obj)

    return str_of_list

def make_dir(directory):
    '''Creates a directory.

    It gives a warning if the directory already exists and skips process.
    The program stops only if there is another problem.

    Parameters
    ----------
    directory : :obj:`string`
        The path to directory which should be created.

    Return
    ------

    '''
    try:
        os.makedirs(directory)
    except OSError as e:
        # errno.EEXIST = directory already exists
        if e.errno == errno.EEXIST:
            print('WARNING: Directory {0} already exists!'.format(directory))
        else:
            raise # re-raise exception if a different error occured

    return

def put_file_to_ecserver(ecd, filename, target, ecuid, ecgid):
    '''Uses the ecaccess-file-put command to send a file to the ECMWF servers.

    Note
    ----
    The return value is just for testing reasons. It does not have
    to be used from the calling function since the whole error handling
    is done in here.

    Parameters
    ----------
    ecd : :obj:`string`
        The path were the file is stored.

    filename : :obj:`string`
        The name of the file to send to the ECMWF server.

    target : :obj:`string`
        The target queue where the file should be sent to.

    ecuid : :obj:`string`
        The user id on ECMWF server.

    ecgid : :obj:`string`
        The group id on ECMWF server.

    Return
    ------

    '''

    try:
        subprocess.check_output(['ecaccess-file-put',
                                 ecd + '/' + filename,
                                 target + ':/home/ms/' +
                                 ecgid + '/' + ecuid +
                                 '/' + filename],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print('... ERROR CODE: ' + str(e.returncode))
        print('... ERROR MESSAGE:\n \t ' + str(e))

        print('\n... Do you have a valid ecaccess certification key?')
        sys.exit('... ECACCESS-FILE-PUT FAILED!')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        print('\n... Most likely the ECACCESS library is not available!')
        sys.exit('... ECACCESS-FILE-PUT FAILED!')

    return

def submit_job_to_ecserver(target, jobname):
    '''Uses ecaccess-job-submit command to submit a job to the ECMWF server.

    Note
    ----
    The return value is just for testing reasons. It does not have
    to be used from the calling function since the whole error handling
    is done in here.

    Parameters
    ----------
    target : :obj:`string`
        The target where the file should be sent to, e.g. the queue.

    jobname : :obj:`string`
        The name of the jobfile to be submitted to the ECMWF server.

    Return
    ------
    job_id : :obj:`int`
        The id number of the job as a reference at the ecmwf server.
    '''

    try:
        job_id = subprocess.check_output(['ecaccess-job-submit', '-queueName',
                                          target, jobname])

    except subprocess.CalledProcessError as e:
        print('... ERROR CODE: ' + str(e.returncode))
        print('... ERROR MESSAGE:\n \t ' + str(e))

        print('\n... Do you have a valid ecaccess certification key?')
        sys.exit('... ECACCESS-JOB-SUBMIT FAILED!')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        print('\n... Most likely the ECACCESS library is not available!')
        sys.exit('... ECACCESS-JOB-SUBMIT FAILED!')

    return job_id


def get_informations(filename):
    '''Gets basic information from an example grib file.

    These information are important for later use and the
    initialization of numpy arrays for data storing.

    Parameters
    ----------
    filename : :obj:`string`
            Name of the file which will be opened to extract basic information.

    Return
    ------
    data : :obj:`dictionary`
        Contains basic informations of the ECMWF grib files, e.g.
        'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
        'longitudeOfFirstGridPointInDegrees', 'latitudeOfLastGridPointInDegrees',
        'longitudeOfLastGridPointInDegrees', 'jDirectionIncrementInDegrees',
        'iDirectionIncrementInDegrees', 'missingValue'
    '''
    from eccodes import codes_grib_new_from_file, codes_get, codes_release

    data = {}

    # --- open file ---
    print("Opening file for getting information data --- %s" % filename)
    with open(filename) as f:
        # load first message from file
        gid = codes_grib_new_from_file(f)

        # information needed from grib message
        keys = [
                'Ni',
                'Nj',
                'latitudeOfFirstGridPointInDegrees',
                'longitudeOfFirstGridPointInDegrees',
                'latitudeOfLastGridPointInDegrees',
                'longitudeOfLastGridPointInDegrees',
                'jDirectionIncrementInDegrees',
                'iDirectionIncrementInDegrees',
                'missingValue',
               ]

        print('\nInformations are: ')
        for key in keys:
            # Get the value of the key in a grib message.
            data[key] = codes_get(gid,key)
            print("%s = %s" % (key,data[key]))

        # Free the memory for the message referred as gribid.
        codes_release(gid)

    return data


def get_dimensions(info, purefc, dtime, index_vals, start_date, end_date):
    '''This function specifies the correct dimensions for x, y and t.

    Parameters
    ----------
    info : :obj:`dictionary`
        Contains basic informations of the ECMWF grib files, e.g.
        'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
        'longitudeOfFirstGridPointInDegrees', 'latitudeOfLastGridPointInDegrees',
        'longitudeOfLastGridPointInDegrees', 'jDirectionIncrementInDegrees',
        'iDirectionIncrementInDegrees', 'missingValue'

    purefc : :obj:`integer`
        Switch for definition of pure forecast mode or not.

    dtime : :obj:`string`
        Time step in hours.

    index_vals : :obj:`list`
        Contains the values from the keys used for a distinct selection
        of grib messages in processing  the grib files.
        Content looks like e.g.:
        index_vals[0]: ('20171106', '20171107', '20171108') ; date
        index_vals[1]: ('0', '1200', '1800', '600') ; time
        index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange

    start_date : :obj:`string`
        The start date of the retrieval job.

    end_date : :obj:`string`
        The end date of the retrieval job.

    Return
    ------
    (ix, jy, it) : :obj:`tuple` of :obj:`integer`
        Dimension in x-direction, y-direction and in time.
    '''

    ix = info['Ni']

    jy = info['Nj']

    if not purefc:
        it = ((end_date - start_date).days + 1) * 24/int(dtime)
    else:
        # #no of step * #no of times * #no of days
        it = len(index_vals[2]) * len(index_vals[1]) * len(index_vals[0])

    return (ix, jy, it)


def execute_subprocess(cmd_list, error_msg='SUBPROCESS FAILED!'):
    '''Executes a command line instruction via a subprocess.

    Error handling is done if an error occures.

    Parameters
    ----------
    cmd_list : :obj:`list` of `:obj:`string`
        A list of the components for the command line execution. Each
        list entry is a single part of the command which is seperated from
        the rest by a blank space.
        E.g. ['mv', file1, file2]

    Return
    ------
    error_msg : :obj:`string`, optional
        The possible error message if the subprocess failed.
        By default it will just tell "SUBPROCESS FAILED!".
    '''

    try:
        subprocess.check_call(cmd_list)
    except subprocess.CalledProcessError as e:
        print('... ERROR CODE: ' + str(e.returncode))
        print('... ERROR MESSAGE:\n \t ' + str(e))

        sys.exit('... ' + error_msg)
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('... ' + error_msg)

    return
