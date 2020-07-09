#!/usr/bin/env python3
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
#    April - December 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - moved all non class methods from former file Flexparttools in here
#        - separated args and control interpretation
#        - added functions get_list_as_string, read_ecenv, send_mail, make_dir,
#          put_file_to_ecserver, submit_job_to_ecserver, get_informations,
#          get_dimensions, execute_subprocess, none_or_int, none_or_str
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
#
# @Methods:
#    none_or_str
#    none_or_int
#    get_cmdline_args
#    read_ecenv
#    clean_up
#    my_error
#    send_mail
#    normal_exit
#    product
#    silent_remove
#    init128
#    to_param_id
#    get_list_as_string
#    make_dir
#    put_file_to_ecserver
#    submit_job_to_ecserver
#    get_informations
#    get_dimensions
#    execute_subprocess
#*******************************************************************************
'''This module contains a collection of diverse tasks within flex_extract.
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import errno
import sys
import glob
import subprocess
import traceback
# pylint: disable=unused-import
try:
    import exceptions
except ImportError:
    import builtins as exceptions
# pylint: enable=unused-import
from datetime import datetime, timedelta
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# ------------------------------------------------------------------------------
# METHODS
# ------------------------------------------------------------------------------

def setup_controldata():
    '''Collects, stores and checks controlling arguments from command line,
    CONTROL file and ECMWF_ENV file.

    Parameters
    ----------

    Return
    ------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    ppid : str
        Parent process id.

    queue : str
        Name of queue for submission to ECMWF (e.g. ecgate or cca )

    job_template : str
        Name of the job template file for submission to ECMWF server.
    '''
    import _config
    from Classes.ControlFile import ControlFile

    args = get_cmdline_args()
    c = ControlFile(args.controlfile)
    c.assign_args_to_control(args)
    if os.path.isfile(_config.PATH_ECMWF_ENV):
        env_parameter = read_ecenv(_config.PATH_ECMWF_ENV)
        c.assign_envs_to_control(env_parameter)
    c.check_conditions(args.queue)

    return c, args.ppid, args.queue, args.job_template

def none_or_str(value):
    '''Converts the input string into Pythons None type if it
    contains the string "None".

    Parameters
    ----------
    value : str
        String to be checked for the "None" word.

    Return
    ------
    None or value:
        Return depends on the content of the input value. If it was "None",
        then the Python type None is returned, otherwise the string itself.
    '''
    if value == 'None':
        return None
    return value

def none_or_int(value):
    '''Converts the input string into Pythons None-type if it
    contains string "None"; otherwise it is converted to an integer value.

    Parameters
    ----------
    value : str
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
    Apply default values for arguments not present.

    Parameters
    ----------

    Return
    ------
    args : Namespace
        Contains the command line arguments from the script / program call.
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
    parser.add_argument("--job_chunk", dest="job_chunk",
                        type=none_or_int, default=None,
                        help="# of days to be retrieved within a single job")
    parser.add_argument("--controlfile", dest="controlfile",
                        type=none_or_str, default='CONTROL_EA5',
                        help="The file with all CONTROL parameters.")
    parser.add_argument("--basetime", dest="basetime",
                        type=none_or_int, default=None,
                        help="base time such as 0 or 12 (for half day retrievals)")
    parser.add_argument("--step", dest="step",
                        type=none_or_str, default=None,
                        help="Forecast steps such as 00/to/48")
    parser.add_argument("--levelist", dest="levelist",
                        type=none_or_str, default=None,
                        help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area",
                        type=none_or_str, default=None,
                        help="area, defined by north/west/south/east")

    # some switches
    parser.add_argument("--debug", dest="debug",
                        type=none_or_int, default=None,
                        help="debug mode - temporary files will be conserved")
    parser.add_argument("--oper", dest="oper",
                        type=none_or_int, default=None,
                        help='operational mode - prepares dates from '
                        'environment variables')
    parser.add_argument("--request", dest="request",
                        type=none_or_int, default=None,
                        help="list all MARS requests in file mars_requests.dat")
    parser.add_argument("--public", dest="public",
                        type=none_or_int, default=None,
                        help="public mode - retrieves public datasets")
    parser.add_argument("--rrint", dest="rrint",
                        type=none_or_int, default=None,
                        help='Selection of old or new  '
                        'interpolation method for precipitation:\n'
                        '     0 - old method\n'
                        '     1 - new method (additional subgrid points)')

    # set directories
    parser.add_argument("--inputdir", dest="inputdir",
                        type=none_or_str, default=None,
                        help='Path to temporary directory for '
                        'retrieved grib files and other processing files.')
    parser.add_argument("--outputdir", dest="outputdir",
                        type=none_or_str, default=None,
                        help='Path to final directory where '
                        'FLEXPART input files will be stored.')

    # this is only used by prepare_flexpart.py to rerun a postprocessing step
    parser.add_argument("--ppid", dest="ppid",
                        type=none_or_str, default=None,
                        help='This is the specify the parent process id of a '
                        'single flex_extract run to identify the files. '
                        'It is the second number in the GRIB files.')

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        type=none_or_str, default="job.temp",
                        help='Job template file. Will be used for submission '
                        'to the batch system on the ECMWF server after '
                        'modification.')
    parser.add_argument("--queue", dest="queue",
                        type=none_or_str, default=None,
                        help='The name of the ECMWF server name where the'
                        'job script is to be submitted ' 
                        '(e.g. ecgate | cca | ccb)')

    args = parser.parse_args()

    return args

def read_ecenv(filepath):
    '''Reads the file into a dictionary where the key values are the parameter
    names.

    Parameters
    ----------
    filepath : str
        Path to file where the ECMWF environment parameters are stored.

    Return
    ------
    envs : dict
        Contains the environment parameter ecuid, ecgid, gateway
        and destination for ECMWF server environments.
    '''
    envs = {}
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
    ECMWF API and keywords "ectrans" or "ecstorage" are set to "1".

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''

    print("... clean inputdir!")

    cleanlist = [filename for filename in
                 glob.glob(os.path.join(c.inputdir, "*"))
                 if not os.path.basename(filename).startswith(c.prefix)]

    if cleanlist:
        for element in cleanlist:
            silent_remove(element)
        print("... done!")
    else:
        print("... nothing to clean!")

    return


def my_error(message='ERROR'):
    '''Prints a specified error message which can be passed to the function
    before exiting the program.

    Parameters
    ----------
    message : str, optional
        Error message. Default value is "ERROR".

    Return
    ------

    '''

    trace = '\n'.join(traceback.format_stack())
    full_message = message + '\n\n' + trace

    print(full_message)

    sys.exit(1)

    return


def send_mail(users, success_mode, message):
    '''Prints a specific exit message which can be passed to the function.

    Parameters
    ----------
    users : list of str
        Contains all email addresses which should be notified.
        It might also contain just the ecmwf user name which wil trigger
        mailing to the associated email address for this user.

    success_mode : str
        States the exit mode of the program to put into
        the mail subject line.

    message : str, optional
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
    message : str, optional
        Message for exiting program. Default value is "Done!".

    Return
    ------

    '''

    print(str(message))

    return


def product(*args, **kwds):
    '''Creates combinations of all passed arguments.

    This method combines the single characters of the passed arguments
    with each other in a way that each character of each argument value
    will be combined with each character of the other arguments as a tuple.

    Note
    ----
    This method is taken from an example at the ECMWF wiki website.
    https://software.ecmwf.int/wiki/display/GRIB/index.py; 2018-03-16

    It was released under the following license:
    https://confluence.ecmwf.int/display/ECC/License

    Example
    -------
    product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy

    product(range(2), repeat = 3) --> 000 001 010 011 100 101 110 111

    Parameters
    ----------
    \*args : list or str
        Positional arguments (arbitrary number).

    \*\*kwds : dict
        Contains all the keyword arguments from \*args.

    Return
    ------
    prod : :obj:`tuple`
        Return will be done with "yield". A tuple of combined arguments.
        See example in description above.
    '''
    try:
        pools = [tuple(arg) for arg in args] * kwds.get('repeat', 1)
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
    filename : str
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
    filepath : str
        Path to file of ECMWF grib table number 128.

    Return
    ------
    table128 : dict
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
            if data != '' and data[0] != '!':
                table128[data[0:3]] = data[59:65].strip()

    return table128


def to_param_id(pars, table):
    '''Transform parameter names to parameter ids with ECMWF grib table 128.

    Parameters
    ----------
    pars : str
        Addpar argument from CONTROL file in the format of
        parameter names instead of IDs. The parameter short
        names are separated by "/" and passed as one single string.

    table : dict
        Contains the ECMWF grib table 128 information.
        The key is the parameter number and the value is the
        short name of the parameter.

    Return
    ------
    ipar : list of int
        List of addpar parameters from CONTROL file transformed to
        parameter ids in the format of integer.
    '''
    if not pars:
        return []
    if not isinstance(pars, str):
        pars = str(pars)

    cpar = pars.upper().split('/')
    ipar = []
    for par in cpar:
        par = par.strip()
        for k, v in table.items():
            if par.isdigit():
                par = str(int(par)).zfill(3)
            if par == k or par == v:
                ipar.append(int(k))
                break
        else:
            print('Warning: par ' + par + ' not found in table 128')

    return ipar

def to_param_id_with_tablenumber(pars, table):
    '''Transform parameter names to parameter IDs and add table ID.

    Conversion with ECMWF grib table 128.

    Parameters
    ----------
    pars : str
        Addpar argument from CONTROL file in the format of
        parameter names instead of ID. The parameter short
        names are separated by "/" and passed as one single string.

    table : dict
        Contains the ECMWF grib table 128 information.
        The key is the parameter number and the value is the
        short name of the parameter.

    Return
    ------
    spar : str
        List of addpar parameters from CONTROL file transformed to
        parameter IDs in the format of integer.
    '''
    if not pars:
        return []
    if not isinstance(pars, str):
        pars = str(pars)

    cpar = pars.upper().split('/')
    spar = []
    for par in cpar:
        for k, v in table.items():
            if par.isdigit():
                par = str(int(par)).zfill(3)
            if par == k or par == v:
                spar.append(k + '.128')
                break
        else:
            print('\n\n\t\tWarning: par ' + par + ' not found in table 128\n\n')

    return '/'.join(spar)

def get_list_as_string(list_obj, concatenate_sign=', '):
    '''Converts a list of arbitrary content into a single string using a given
    concatenation character.

    Parameters
    ----------
    list_obj : list of *
        A list with arbitrary content.

    concatenate_sign : str, optional
        A string which is used to concatenate the single
        list elements. Default value is ", ".

    Return
    ------
    str_of_list : str
        The content of the list as a single string.
    '''

    if not isinstance(list_obj, list):
        list_obj = list(list_obj)
    str_of_list = concatenate_sign.join(str(l) for l in list_obj)

    return str_of_list

def make_dir(directory):
    '''Creates a directory.

    If the directory already exists, an information is printed and the creation 
    skipped. The program stops only if there is another problem.

    Parameters
    ----------
    directory : str
        The path to directory which should be created.

    Return
    ------

    '''
    try:
        os.makedirs(directory)
    except OSError as e:
        # errno.EEXIST = directory already exists
        if e.errno == errno.EEXIST:
            print('INFORMATION: Directory {0} already exists!'.format(directory))
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
    ecd : str
        The path were the file is stored.

    filename : str
        The name of the file to send to the ECMWF server.

    target : str
        The target queue where the file should be sent to.

    ecuid : str
        The user id on ECMWF server.

    ecgid : str
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
    target : str
        The target where the file should be sent to, e.g. the queue.

    jobname : str
        The name of the jobfile to be submitted to the ECMWF server.

    Return
    ------
    job_id : int
        The id number of the job as a reference at the ECMWF server.
    '''

    try:
        job_id = subprocess.check_output(['ecaccess-job-submit', '-queueName',
                                          target, jobname])

    except subprocess.CalledProcessError as e:
        print('... ERROR CODE: ' + str(e.returncode))
        print('... ERROR MESSAGE:\n \t ' + str(e))

        print('\n... Do you have a valid ecaccess certification key?')
        sys.exit('... ecaccess-job-submit FAILED!')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        print('\n... Most likely the ECACCESS library is not available!')
        sys.exit('... ecaccess-job-submit FAILED!')

    return job_id.decode()


def get_informations(filename):
    '''Extracts basic information from a sample grib file.

    This information is needed for later use and the
    initialization of numpy arrays where data are stored.

    Parameters
    ----------
    filename : str
            Name of the file which will be opened to extract basic information.

    Return
    ------
    data : dict
        Contains basic informations of the ECMWF grib files, e.g.
        'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
        'longitudeOfFirstGridPointInDegrees', 'latitudeOfLastGridPointInDegrees',
        'longitudeOfLastGridPointInDegrees', 'jDirectionIncrementInDegrees',
        'iDirectionIncrementInDegrees', 'missingValue'
    '''
    from eccodes import codes_grib_new_from_file, codes_get, codes_release

    data = {}

    # --- open file ---
    print("Opening grib file for extraction of information --- %s" % filename)
    with open(filename, 'rb') as f:
        # load first message from file
        gid = codes_grib_new_from_file(f)

        # information needed from grib message
        keys = ['Ni',
                'Nj',
                'latitudeOfFirstGridPointInDegrees',
                'longitudeOfFirstGridPointInDegrees',
                'latitudeOfLastGridPointInDegrees',
                'longitudeOfLastGridPointInDegrees',
                'jDirectionIncrementInDegrees',
                'iDirectionIncrementInDegrees',
                'missingValue',
               ]

        print('\nInformation extracted: ')
        for key in keys:
            # Get the value of the key in a grib message.
            data[key] = codes_get(gid, key)
            print("%s = %s" % (key, data[key]))

        # Free the memory for the message referred as gribid.
        codes_release(gid)

    return data


def get_dimensions(info, purefc, dtime, index_vals, start_date, end_date):
    '''This function specifies the correct dimensions for x, y, and t.

    Parameters
    ----------
    info : dict
        Contains basic informations of the ECMWF grib files, e.g.
        'Ni', 'Nj', 'latitudeOfFirstGridPointInDegrees',
        'longitudeOfFirstGridPointInDegrees', 'latitudeOfLastGridPointInDegrees',
        'longitudeOfLastGridPointInDegrees', 'jDirectionIncrementInDegrees',
        'iDirectionIncrementInDegrees', 'missingValue'

    purefc : int
        Switch for definition of pure forecast mode or not.

    dtime : str
        Time step in hours.

    index_vals : list of list of str
        Contains the values from the keys used for a distinct selection
        of GRIB messages in processing the grib files.
        Content looks like e.g.:
        index_vals[0]: ('20171106', '20171107', '20171108') ; date
        index_vals[1]: ('0', '1200', '1800', '600') ; time
        index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange

    start_date : str
        The start date of the retrieval job.

    end_date : str
        The end date of the retrieval job.

    Return
    ------
    (ix, jy, it) : tuple of int
        Dimension in x-direction, y-direction and in time.
    '''

    ix = info['Ni']

    jy = info['Nj']

    if not purefc:
        it = ((end_date - start_date).days + 1) * 24 // int(dtime)
    else:
        # #no of step * #no of times * #no of days
        it = len(index_vals[2]) * len(index_vals[1]) * len(index_vals[0])

    return (ix, jy, it)


def execute_subprocess(cmd_list, error_msg='SUBPROCESS FAILED!'):
    '''Executes a command via a subprocess.

    Error handling is done if an error occures.

    Parameters
    ----------
    cmd_list : list of str
        A list of the components for the command line execution. 
        They will be concatenated with blank space for the command 
        to be submitted, like ['mv', file1, file2] for mv file1 file2.

    Return
    ------
    error_msg : str, optional
        Error message if the subprocess fails.
        By default it will just say "SUBPROCESS FAILED!".
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


def generate_retrieval_period_boundary(c):
    '''Generates retrieval period boundary datetimes from CONTROL information.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------
    start_period : datetime
        The first timestamp of the actual retrieval period disregarding
        the temporary times which were used for processing reasons.

    end_period : datetime
        The last timestamp of the actual retrieval period disregarding
        the temporary times which were used for processing reasons.
    '''
    # generate start and end timestamp of the retrieval period
    start_period = datetime.strptime(c.start_date + c.time[0], '%Y%m%d%H')
    start_period = start_period + timedelta(hours=int(c.step[0]))
    end_period = datetime.strptime(c.end_date + c.time[-1], '%Y%m%d%H')
    end_period = end_period + timedelta(hours=int(c.step[-1]))


    return start_period, end_period
