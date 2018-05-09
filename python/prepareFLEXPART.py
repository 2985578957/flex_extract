#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - Change History ist nicht angepasst ans File! Original geben lassen
# - wieso cleanup in main wenn es in prepareflexpart bereits abgefragt wurde?
#   doppelt gemoppelt?
# - wieso start=startm1 wenn basetime = 0 ?  wenn die fluxes nicht mehr
#   relevant sind? verstehe ich nicht
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: October 2014

@ChangeHistory:
    November 2015 - Leopold Haimberger (University of Vienna):
        - using the WebAPI also for general MARS retrievals
        - job submission on ecgate and cca
        - job templates suitable for twice daily operational dissemination
        - dividing retrievals of longer periods into digestable chunks
        - retrieve also longer term forecasts, not only analyses and
          short term forecast data
        - conversion into GRIB2
        - conversion into .fp format for faster execution of FLEXPART

    February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - minor changes in programming style for consistence
        - BUG: removed call of cleanup-Function after call of prepareFlexpart
                since it is already called in prepareFlexpart at the end!

@License:
    (C) Copyright 2014-2018.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    - A standard python 2.6 or 2.7 installation
    - dateutils
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
import calendar
import shutil
import datetime
import time
import os
import inspect
import sys
import socket
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import UIOFiles
import Control
import Tools
import ECFlexpart

hostname = socket.gethostname()
ecapi = 'ecmwf' not in hostname
try:
    if ecapi:
        import ecmwfapi
except ImportError:
    ecapi = False

# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)
# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def prepareFLEXPART(args, c):
    '''
    @Description:


    @Input:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

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

    if not args.ppid:
        c.ppid = str(os.getppid())
    else:
        c.ppid = args.ppid

    c.ecapi = ecapi

    # create the start and end date
    start = datetime.date(year=int(c.start_date[:4]),
                          month=int(c.start_date[4:6]),
                          day=int(c.start_date[6:]))

    end = datetime.date(year=int(c.end_date[:4]),
                        month=int(c.end_date[4:6]),
                        day=int(c.end_date[6:]))

    # to deaccumulate the fluxes correctly
    # one day ahead of the start date and
    # one day after the end date is needed
    startm1 = start - datetime.timedelta(days=1)
    endp1 = end + datetime.timedelta(days=1)

    # get all files with flux data to be deaccumulated
    inputfiles = UIOFiles.UIOFiles(['.grib', '.grb', '.grib1',
                           '.grib2', '.grb1', '.grb2'])

    inputfiles.listFiles(c.inputdir, '*OG_acc_SL*.' + c.ppid + '.*')

    # create output dir if necessary
    if not os.path.exists(c.outputdir):
        os.makedirs(c.outputdir)

    # deaccumulate the flux data
    flexpart = ECFlexpart.ECFlexpart(c, fluxes=True)
    flexpart.write_namelist(c, 'fort.4')
    flexpart.deacc_fluxes(inputfiles, c)

    print('Prepare ' + start.strftime("%Y%m%d") +
          "/to/" + end.strftime("%Y%m%d"))

    # get a list of all files from the root inputdir
    inputfiles = UIOFiles.UIOFiles(['.grib', '.grb', '.grib1',
                           '.grib2', '.grb1', '.grb2'])

    inputfiles.listFiles(c.inputdir, '????__??.*' + c.ppid + '.*')

    # produce FLEXPART-ready GRIB files and
    # process GRIB files -
    # copy/transfer/interpolate them or make them GRIB2
    if c.basetime == '00':
        start = startm1

    flexpart = ECFlexpart.ECFlexpart(c, fluxes=False)
    flexpart.create(inputfiles, c)
    flexpart.process_output(c)

    # check if in debugging mode, then store all files
    # otherwise delete temporary files
    if int(c.debug) != 0:
        print('Temporary files left intact')
    else:
        Tools.cleanup(c)

    return

if __name__ == "__main__":
    args, c = Tools.interpret_args_and_control()
    prepareFLEXPART(args, c)
