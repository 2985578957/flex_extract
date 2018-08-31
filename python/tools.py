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
#    - get_cmdline_arguments
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
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

def get_cmdline_arguments():
    '''
    @Description:
        Decomposes the command line arguments and assigns them to variables.
        Apply default values for non mentioned arguments.

    @Input:
        <nothing>

    @Return:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.
    '''

    parser = ArgumentParser(description='Retrieve FLEXPART input from \
                                ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # the most important arguments
    parser.add_argument("--start_date", dest="start_date", default=None,
                        help="start date YYYYMMDD")
    parser.add_argument("--end_date", dest="end_date", default=None,
                        help="end_date YYYYMMDD")
    parser.add_argument("--date_chunk", dest="date_chunk", default=None,
                        help="# of days to be retrieved at once")

    # some arguments that override the default in the CONTROL file
    parser.add_argument("--basetime", dest="basetime", default=None,
                        help="base such as 00/12 (for half day retrievals)")
    parser.add_argument("--step", dest="step", default=None,
                        help="steps such as 00/to/48")
    parser.add_argument("--levelist", dest="levelist", default=None,
                        help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area", default=None,
                        help="area defined as north/west/south/east")

    # set the working directories
    parser.add_argument("--inputdir", dest="inputdir", default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir", default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        default=None,
                        help="FLEXPART root directory (to find grib2flexpart \
                        and COMMAND file)\n Normally flex_extract resides in \
                        the scripts directory of the FLEXPART distribution")

    # this is only used by prepare_flexpart.py to rerun a postprocessing step
    parser.add_argument("--ppid", dest="ppid", default=None,
                        help="specify parent process id for \
                        rerun of prepare_flexpart")

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        default="job.temp",
                        help="job template file for submission to ECMWF")
    parser.add_argument("--queue", dest="queue", default=None,
                        help="queue for submission to ECMWF \
                        (e.g. ecgate or cca )")
    parser.add_argument("--controlfile", dest="controlfile",
                        default='CONTROL.temp',
                        help="file with CONTROL parameters")
    parser.add_argument("--debug", dest="debug", default=None,
                        help="debug mode - leave temporary files intact")

    args = parser.parse_args()

    return args

def read_ecenv(filename):
    '''
    @Description:
        Reads the file into a dictionary where the key values are the parameter
        names.

    @Input:
        filename: string
            Name of file where the ECMWV environment parameters are stored.

    @Return:
        envs: dict
    '''
    envs= {}
    print filename
    with open(filename, 'r') as f:
        for line in f:
            data = line.strip().split()
            envs[str(data[0])] = str(data[1])

    return envs

def clean_up(c):
    '''
    @Description:
        Remove all files from intermediate directory
        (inputdir from CONTROL file).

    @Input:
        c: instance of class ControlFile
            Contains all the parameters of CONTROL file, which are e.g.:
            DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
            STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
            LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
            OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
            ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
            MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
            DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

            For more information about format and content of the parameter
            see documentation.

    @Return:
        <nothing>
    '''

    print "clean_up"

    cleanlist = glob.glob(c.inputdir + "/*")
    for clist in cleanlist:
        if c.prefix not in clist:
            silent_remove(clist)
        if c.ecapi is False and (c.ectrans == '1' or c.ecstorage == '1'):
            silent_remove(clist)

    print "Done"

    return


def my_error(users, message='ERROR'):
    '''
    @Description:
        Prints a specified error message which can be passed to the function
        before exiting the program.

    @Input:
        user: list of strings
            Contains all email addresses which should be notified.
            It might also contain just the ecmwf user name which wil trigger
            mailing to the associated email address for this user.

        message: string, optional
            Error message. Default value is "ERROR".

    @Return:
        <nothing>
    '''

    print message

    # comment if user does not want email notification directly from python
    for user in users:
        if '${USER}' in user:
            user = os.getenv('USER')
        try:
            p = subprocess.Popen(['mail', '-s flex_extract_v7.1 ERROR',
                                  os.path.expandvars(user)],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 bufsize=1)
            trace = '\n'.join(traceback.format_stack())
            pout = p.communicate(input=message + '\n\n' + trace)[0]
        except ValueError as e:
            print 'ERROR: ', e
            sys.exit('Email could not be sent!')
        else:
            print 'Email sent to ' + os.path.expandvars(user) + ' ' + \
                  pout.decode()

    sys.exit(1)

    return


def normal_exit(users, message='Done!'):
    '''
    @Description:
        Prints a specific exit message which can be passed to the function.

    @Input:
        user: list of strings
            Contains all email addresses which should be notified.
            It might also contain just the ecmwf user name which wil trigger
            mailing to the associated email address for this user.

        message: string, optional
            Message for exiting program. Default value is "Done!".

    @Return:
        <nothing>

    '''
    print message

    # comment if user does not want notification directly from python
    for user in users:
        if '${USER}' in user:
            user = os.getenv('USER')
        try:
            p = subprocess.Popen(['mail', '-s flex_extract_v7.1 normal exit',
                                  os.path.expandvars(user)],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 bufsize=1)
            pout = p.communicate(input=message+'\n\n')[0]
        except ValueError as e:
            print 'ERROR: ', e
            print 'Email could not be sent!'
        else:
            print 'Email sent to ' + os.path.expandvars(user) + ' ' + \
                  pout.decode()

    return


def product(*args, **kwds):
    '''
    @Description:
        This method is taken from an example at the ECMWF wiki website.
        https://software.ecmwf.int/wiki/display/GRIB/index.py; 2018-03-16

        This method combines the single characters of the passed arguments
        with each other. So that each character of each argument value
        will be combined with each character of the other arguments as a tuple.

        Example:
        product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        product(range(2), repeat = 3) --> 000 001 010 011 100 101 110 111

    @Input:
        *args: tuple
            Positional arguments (arbitrary number).

        **kwds: dictionary
            Contains all the keyword arguments from *args.

    @Return:
        prod: tuple
            Return will be done with "yield". A tuple of combined arguments.
            See example in description above.
    '''
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x + [y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)

    return


def silent_remove(filename):
    '''
    @Description:
        If "filename" exists , it is removed.
        The function does not fail if the file does not exist.

    @Input:
        filename: string
            The name of the file to be removed without notification.

    @Return:
        <nothing>
    '''
    try:
        os.remove(filename)
    except OSError as e:
        # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:
            # errno.ENOENT  =  no such file or directory
            raise  # re-raise exception if a different error occured

    return


def init128(filepath):
    '''
    @Description:
        Opens and reads the grib file with table 128 information.

    @Input:
        filepath: string
            Path to file of ECMWF grib table number 128.

    @Return:
        table128: dictionary
            Contains the ECMWF grib table 128 information.
            The key is the parameter number and the value is the
            short name of the parameter.
    '''
    table128 = dict()
    with open(filepath) as f:
        fdata = f.read().split('\n')
    for data in fdata:
        if data[0] != '!':
            table128[data[0:3]] = data[59:64].strip()

    return table128


def to_param_id(pars, table):
    '''
    @Description:
        Transform parameter names to parameter ids
        with ECMWF grib table 128.

    @Input:
        pars: string
            Addpar argument from CONTROL file in the format of
            parameter names instead of ids. The parameter short
            names are sepearted with "/" and they are passed as
            one single string.

        table: dictionary
            Contains the ECMWF grib table 128 information.
            The key is the parameter number and the value is the
            short name of the parameter.

    @Return:
        ipar: list of integer
            List of addpar parameters from CONTROL file transformed to
            parameter ids in the format of integer.
    '''
    cpar = pars.upper().split('/')
    ipar = []
    for par in cpar:
        for k, v in table.iteritems():
            if par == k or par == v:
                ipar.append(int(k))
                break
        else:
            print 'Warning: par ' + par + ' not found in table 128'

    return ipar

def get_list_as_string(list_obj, concatenate_sign=', '):
    '''
    @Description:
        Converts a list of arbitrary content into a single string.

    @Input:
        list_obj: list
            A list with arbitrary content.

        concatenate_sign: string, optional
            A string which is used to concatenate the single
            list elements. Default value is ", ".

    @Return:
        str_of_list: string
            The content of the list as a single string.
    '''

    str_of_list = concatenate_sign.join(str(l) for l in list_obj)

    return str_of_list

def make_dir(directory):
    '''
    @Description:
        Creates a directory and gives a warning if the directory
        already exists. The program stops only if there is another problem.

    @Input:
        directory: string
            The directory path which should be created.

    @Return:
        <nothing>
    '''
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            # errno.EEXIST = directory already exists
            raise # re-raise exception if a different error occured
        else:
            print 'WARNING: Directory {0} already exists!'.format(directory)

    return

def put_file_to_ecserver(ecd, filename, target, ecuid, ecgid):
    '''
    @Description:
        Uses the ecaccess command to send a file to the ECMWF servers.
        Catches and prints the error if it failed.

    @Input:
        ecd: string
            The path were the file is to be stored.

        filename: string
            The name of the file to send to the ECMWF server.

        target: string
            The target where the file should be sent to, e.g. the queue.

        ecuid: string
            The user id on ECMWF server.

        ecgid: string
            The group id on ECMWF server.

    @Return:
        <nothing>
    '''

    try:
        subprocess.check_call(['ecaccess-file-put',
                               ecd + '../' + filename,
                               target + ':/home/ms/' +
                               ecgid + '/' + ecuid +
                               '/' + filename])
    except subprocess.CalledProcessError as e:
        print 'ERROR:'
        print e
        sys.exit('ecaccess-file-put failed!\n' + \
                 'Probably the eccert key has expired.')

    return

def submit_job_to_ecserver(target, jobname):
    '''
    @Description:
        Uses ecaccess to submit a job to the ECMWF server.
        Catches and prints the error if one arise.

    @Input:
        target: string
            The target where the file should be sent to, e.g. the queue.

        jobname: string
            The name of the jobfile to be submitted to the ECMWF server.

    @Return:
        rcode: integer
            Resulting code of subprocess.check_call.
    '''

    try:
        rcode = subprocess.check_call(['ecaccess-job-submit',
                                       '-queueName', target,
                                       jobname])
    except subprocess.CalledProcessError as e:
        print '... ERROR CODE: ', e.returncode
        sys.exit('... ECACCESS-JOB-SUBMIT FAILED!')

    return rcode
