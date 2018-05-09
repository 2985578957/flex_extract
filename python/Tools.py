#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# -
#************************************************************************
"""

"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import os
import errno
import sys
import glob
from numpy import *
from gribapi import *
import Control

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

def interpret_args_and_control():
    '''
    @Description:
        Assigns the command line arguments and reads control file
        content. Apply default values for non mentioned arguments.

    @Input:
        <nothing>

    @Return:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

        c: instance of class Control
            Contains all necessary information of a control file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, DEBUG, INPUTDIR,
            OUTPUTDIR, FLEXPART_ROOT_SCRIPTS
            For more information about format and content of the parameter see
            documentation.

    '''
    parser = ArgumentParser(description='Retrieve FLEXPART input from \
                            ECMWF MARS archive',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    # the most important arguments
    parser.add_argument("--start_date", dest="start_date",
                        help="start date YYYYMMDD")
    parser.add_argument("--end_date", dest="end_date",
                        help="end_date YYYYMMDD")
    parser.add_argument("--date_chunk", dest="date_chunk", default=None,
                        help="# of days to be retrieved at once")

    # some arguments that override the default in the control file
    parser.add_argument("--basetime", dest="basetime",
                        help="base such as 00/12 (for half day retrievals)")
    parser.add_argument("--step", dest="step",
                        help="steps such as 00/to/48")
    parser.add_argument("--levelist", dest="levelist",
                        help="Vertical levels to be retrieved, e.g. 30/to/60")
    parser.add_argument("--area", dest="area",
                        help="area defined as north/west/south/east")

    # set the working directories
    parser.add_argument("--inputdir", dest="inputdir", default=None,
                        help="root directory for storing intermediate files")
    parser.add_argument("--outputdir", dest="outputdir", default=None,
                        help="root directory for storing output files")
    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory (to find grib2flexpart \
                        and COMMAND file)\n\ Normally ECMWFDATA resides in \
                        the scripts directory of the FLEXPART distribution")

    # this is only used by prepareFLEXPART.py to rerun a postprocessing step
    parser.add_argument("--ppid", dest="ppid",
                        help="Specify parent process id for \
                        rerun of prepareFLEXPART")

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        default="job.temp",
                        help="job template file for submission to ECMWF")
    parser.add_argument("--queue", dest="queue",
                        help="queue for submission to ECMWF \
                        (e.g. ecgate or cca )")
    parser.add_argument("--controlfile", dest="controlfile",
                        default='CONTROL.temp',
                        help="file with control parameters")
    parser.add_argument("--debug", dest="debug", default=0,
                        help="Debug mode - leave temporary files intact")

    args = parser.parse_args()

    # create instance of Control for specified controlfile
    # and assign the parameters (and default values if necessary)
    try:
        c = Control.Control(args.controlfile)
    except IOError:
        try:
            c = Control.Control(localpythonpath + args.controlfile)
        except:
            print('Could not read control file "' + args.controlfile + '"')
            print('Either it does not exist or its syntax is wrong.')
            print('Try "' + sys.argv[0].split('/')[-1] +
                  ' -h" to print usage information')
            exit(1)

    # check for having at least a starting date
    if  args.start_date is None and getattr(c, 'start_date') is None:
        print('start_date specified neither in command line nor \
               in control file ' + args.controlfile)
        print('Try "' + sys.argv[0].split('/')[-1] +
              ' -h" to print usage information')
        exit(1)

    # save all existing command line parameter to the Control instance
    # if parameter is not specified through the command line or CONTROL file
    # set default values
    if args.start_date is not None:
        c.start_date = args.start_date
    if args.end_date is not None:
        c.end_date = args.end_date
    if c.end_date is None:
        c.end_date = c.start_date
    if args.date_chunk is not None:
        c.date_chunk = args.date_chunk

    if not hasattr(c, 'debug'):
        c.debug = args.debug

    if args.inputdir is None and args.outputdir is None:
        c.inputdir = '../work'
        c.outputdir = '../work'
    else:
        if args.inputdir is not None:
            c.inputdir = args.inputdir
        if args.outputdir is None:
            c.outputdir = args.inputdir
        if args.outputdir is not None:
            c.outputdir = args.outputdir
        if args.inputdir is None:
            c.inputdir = args.outputdir

    if hasattr(c, 'outputdir') is False and args.outputdir is None:
        c.outputdir = c.inputdir
    else:
        if args.outputdir is not None:
            c.outputdir = args.outputdir

    if args.area is not None:
        afloat = '.' in args.area
        l = args.area.split('/')
        if afloat:
            for i in range(len(l)):
                l[i] = str(int(float(l[i]) * 1000))
        c.upper, c.left, c.lower, c.right = l

    # NOTE: basetime activates the ''operational mode''
    if args.basetime is not None:
        c.basetime = args.basetime

    if args.step is not None:
        l = args.step.split('/')
        if 'to' in args.step.lower():
            if 'by' in args.step.lower():
                ilist = arange(int(l[0]), int(l[2]) + 1, int(l[4]))
                c.step = ['{:0>3}'.format(i) for i in ilist]
            else:
                myerror(None, args.step + ':\n' +
                        'please use "by" as well if "to" is used')
        else:
            c.step = l

    if args.levelist is not None:
        c.levelist = args.levelist
        if 'to' in c.levelist:
            c.level = c.levelist.split('/')[2]
        else:
            c.level = c.levelist.split('/')[-1]

    if args.flexpart_root_scripts is not None:
        c.flexpart_root_scripts = args.flexpart_root_scripts

    return args, c


def cleanup(c):
    '''
    @Description:
        Remove all files from intermediate directory
        (inputdir from control file).

    @Input:
        c: instance of class Control
            Contains all the parameters of control files, which are e.g.:
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

    print("cleanup")

    cleanlist = glob.glob(c.inputdir + "/*")
    for cl in cleanlist:
        if c.prefix not in cl:
            silentremove(cl)
        if c.ecapi is False and (c.ectrans == '1' or c.ecstorage == '1'):
            silentremove(cl)

    print("Done")

    return


def myerror(c, message='ERROR'):
    '''
    @Description:
        Prints a specified error message which can be passed to the function
        before exiting the program.

    @Input:
        c: instance of class Control
            Contains all the parameters of control files, which are e.g.:
            DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
            STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
            LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
            OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
            ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
            MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
            DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

            For more information about format and content of the parameter
            see documentation.

        message: string, optional
            Error message. Default value is "ERROR".

    @Return:
        <nothing>
    '''
    # uncomment if user wants email notification directly from python
    #try:
        #target = c.mailfail
    #except AttributeError:
        #target = os.getenv('USER')

    #if(type(target) is not list):
        #target = [target]

    print(message)

    # uncomment if user wants email notification directly from python
    #for t in target:
    #p = subprocess.Popen(['mail','-s ECMWFDATA v7.0 ERROR', os.path.expandvars(t)],
    #                     stdin = subprocess.PIPE, stdout = subprocess.PIPE,
    #                     stderr = subprocess.PIPE, bufsize = 1)
    #tr = '\n'.join(traceback.format_stack())
    #pout = p.communicate(input = message+'\n\n'+tr)[0]
    #print 'Email sent to '+os.path.expandvars(t) # +' '+pout.decode()

    exit(1)

    return


def normalexit(c, message='Done!'):
    '''
    @Description:
        Prints a specific exit message which can be passed to the function.

    @Input:
        c: instance of class Control
            Contains all the parameters of control files, which are e.g.:
            DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
            STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
            LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
            OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
            ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
            MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
            DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

            For more information about format and content of the parameter
            see documentation.

        message: string, optional
            Message for exiting program. Default value is "Done!".

    @Return:
        <nothing>

    '''
    # Uncomment if user wants notification directly from python
    #try:
        #target = c.mailops
        #if(type(target) is not list):
            #target = [target]
        #for t in target:
            #p = subprocess.Popen(['mail','-s ECMWFDATA v7.0 normal exit',
            #                      os.path.expandvars(t)],
            #                      stdin = subprocess.PIPE,
            #                      stdout = subprocess.PIPE,
            #                      stderr = subprocess.PIPE, bufsize = 1)
            #pout = p.communicate(input = message+'\n\n')[0]
            #print pout.decode()
    #except:
        #pass

    print(message)

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


def silentremove(filename):
    '''
    @Description:
        Removes the file which name is passed to the function if
        it exists. The function does not fail if the file does not
        exist.

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
        if e.errno is not  errno.ENOENT:
            # errno.ENOENT  =  no such file or directory
            raise  # re-raise exception if a different error occured

    return


def init128(fn):
    '''
    @Description:
        Opens and reads the grib file with table 128 information.

    @Input:
        fn: string
            Path to file of ECMWF grib table number 128.

    @Return:
        table128: dictionary
            Contains the ECMWF grib table 128 information.
            The key is the parameter number and the value is the
            short name of the parameter.
    '''
    table128 = dict()
    with open(fn) as f:
        fdata = f.read().split('\n')
    for data in fdata:
        if data[0] != '!':
            table128[data[0:3]] = data[59:64].strip()

    return table128


def toparamId(pars, table):
    '''
    @Description:
        Transform parameter names to parameter ids
        with ECMWF grib table 128.

    @Input:
        pars: string
            Addpar argument from control file in the format of
            parameter names instead of ids. The parameter short
            names are sepearted with "/" and they are passed as
            one single string.

        table: dictionary
            Contains the ECMWF grib table 128 information.
            The key is the parameter number and the value is the
            short name of the parameter.

    @Return:
        ipar: list of integer
            List of addpar parameters from control file transformed to
            parameter ids in the format of integer.
    '''
    cpar = pars.upper().split('/')
    ipar = []
    for par in cpar:
        found = False
        for k, v in table.iteritems():
            if par == k or par == v:
                ipar.append(int(k))
                found = True
                break
        if found is False:
            print('Warning: par ' + par + ' not found in table 128')

    return ipar

def getListAsString(listobj):
    '''
    @Description:
    '''
    return ", ".join( str(l) for l in listobj)