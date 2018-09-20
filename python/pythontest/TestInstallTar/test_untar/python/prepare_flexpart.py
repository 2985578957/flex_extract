#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - using the WebAPI also for general MARS retrievals
#        - job submission on ecgate and cca
#        - job templates suitable for twice daily operational dissemination
#        - dividing retrievals of longer periods into digestable chunks
#        - retrieve also longer term forecasts, not only analyses and
#          short term forecast data
#        - conversion into GRIB2
#        - conversion into .fp format for faster execution of FLEXPART
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - minor changes in programming style for consistence
#        - BUG: removed call of clean_up-Function after call of
#               prepareFlexpart in main since it is already called in
#               prepareFlexpart at the end!
#        - created function main and moved the two function calls for
#          arguments and prepare_flexpart into it
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program Functionality:
#    This program prepares the final version of the grib files which are
#    then used by FLEXPART. It converts the bunch of grib files extracted
#    via get_mars_data by doing for example the necessary conversion to get
#    consistent grids or the disaggregation of flux data. Finally, the
#    program combines the data fields in files per available hour with the
#    naming convention xxYYMMDDHH, where xx should be 2 arbitrary letters
#    (mostly xx is chosen to be "EN").
#
# @Program Content:
#    - main
#    - prepare_flexpart
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import datetime
import os
import inspect
import sys
import socket
import _config

# software specific classes and modules from flex_extract
from UioFiles import UioFiles
from tools import clean_up, get_cmdline_arguments, read_ecenv
from EcFlexpart import EcFlexpart

ecapi = 'ecmwf' not in socket.gethostname()
try:
    if ecapi:
        import ecmwfapi
except ImportError:
    ecapi = False

# add path to pythonpath so that python finds its buddies
LOCAL_PYTHON_PATH = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if LOCAL_PYTHON_PATH not in sys.path:
    sys.path.append(LOCAL_PYTHON_PATH)


# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''
    @Description:
        If prepare_flexpart is called from command line, this function controls
        the program flow and calls the argumentparser function and
        the prepare_flexpart function for preparation of GRIB data for FLEXPART.

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''

    args = get_cmdline_arguments()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        try:
            c = ControlFile(LOCAL_PYTHON_PATH + args.controlfile)
        except IOError:
            print 'Could not read CONTROL file "' + args.controlfile + '"'
            print 'Either it does not exist or its syntax is wrong.'
            print 'Try "' + sys.argv[0].split('/')[-1] + \
                  ' -h" to print usage information'
            sys.exit(1)

    env_parameter = read_ecenv(c.ecmwfdatadir + 'python/ECMWF_ENV')
    c.assign_args_to_control(args, env_parameter)
    c.assign_envs_to_control(env_parameter)
    c.check_conditions()
    prepare_flexpart(args.ppid, c)

    return

def prepare_flexpart(ppid, c):
    '''
    @Description:
        Lists all grib files retrieved from MARS with get_mars_data and
        uses prepares data for the use in FLEXPART. Specific data fields
        are converted to a different grid and the flux data are going to be
        disaggregated. The data fields are collected by hour and stored in
        a file with a specific FLEXPART relevant naming convention.

    @Input:
        ppid: int
            Contains the ppid number of the current ECMWF job. If it is called
            from this script, it is "None".

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

    if not ppid:
        c.ppid = str(os.getppid())
    else:
        c.ppid = ppid

    c.ecapi = ecapi

    # create the start and end date
    start = datetime.date(year=int(c.start_date[:4]),
                          month=int(c.start_date[4:6]),
                          day=int(c.start_date[6:]))

    end = datetime.date(year=int(c.end_date[:4]),
                        month=int(c.end_date[4:6]),
                        day=int(c.end_date[6:]))

    # assign starting date minus 1 day
    # since for basetime 00 we need the 12 hours upfront
    # (the day before from 12 UTC to current day 00 UTC)
    if c.basetime == '00':
        start = start - datetime.timedelta(days=1)

    print 'Prepare ' + start.strftime("%Y%m%d") + \
           "/to/" + end.strftime("%Y%m%d")

    # create output dir if necessary
    if not os.path.exists(c.outputdir):
        os.makedirs(c.outputdir)

    # get all files with flux data to be deaccumulated
    inputfiles = UioFiles(c.inputdir, '*OG_acc_SL*.' + c.ppid + '.*')

    # deaccumulate the flux data
    flexpart = EcFlexpart(c, fluxes=True)
    flexpart.write_namelist(c, 'fort.4')
    flexpart.deacc_fluxes(inputfiles, c)

    # get a list of all files from the root inputdir
    inputfiles = UioFiles(c.inputdir, '????__??.*' + c.ppid + '.*')

    # produce FLEXPART-ready GRIB files and process them -
    # copy/transfer/interpolate them or make them GRIB2
    flexpart = EcFlexpart(c, fluxes=False)
    flexpart.create(inputfiles, c)
    flexpart.process_output(c)

    # check if in debugging mode, then store all files
    # otherwise delete temporary files
    if int(c.debug) != 0:
        print '\nTemporary files left intact'
    else:
        clean_up(c)

    return

if __name__ == "__main__":
    main()
