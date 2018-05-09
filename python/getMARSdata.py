#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
# - Change History ist nicht angepasst ans File!
# - add file description
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

"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
try:
    ecapi=True
    import ecmwfapi
except ImportError:
    ecapi=False

import calendar
import shutil
import datetime
import time
import os
import glob
import sys
import inspect
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)

from Control import Control
from Tools import myerror, normalexit, \
                          interpret_args_and_control
from ECFlexpart import ECFlexpart

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def getMARSdata(args, c):


    if not os.path.exists(c.inputdir):
        os.makedirs(c.inputdir)
    print("start date %s " % (c.start_date))
    print("end date %s " % (c.end_date))

    if ecapi:
        server = ecmwfapi.ECMWFService("mars")
    else:
        server = False

    c.ecapi = ecapi
    print 'ecapi:', c.ecapi

# Retrieve EC data for running flexpart
#AP change this variant to correct format conversion with datetime
#AP import datetime and timedelta explicitly
    syear = int(c.start_date[:4])
    smonth = int(c.start_date[4:6])
    sday = int(c.start_date[6:])
    start = datetime.date(year=syear, month=smonth, day=sday)
    startm1 = start - datetime.timedelta(days=1)
    if c.basetime == '00':
        start = startm1

    eyear = int(c.end_date[:4])
    emonth = int(c.end_date[4:6])
    eday = int(c.end_date[6:])
    end = datetime.date(year=eyear, month=emonth, day=eday)
    if c.basetime == '00' or c.basetime == '12':
        endp1 = end + datetime.timedelta(days=1)
    else:
        endp1 = end + datetime.timedelta(days=2)

    datechunk = datetime.timedelta(days=int(c.date_chunk))

    # retrieving of accumulated data fields (flux data), (maximum one month)

    # remove old files
    print 'removing content of ' + c.inputdir
    tobecleaned = glob.glob(c.inputdir + '/*_acc_*.' + \
                            str(os.getppid()) + '.*.grb')
    for f in tobecleaned:
        os.remove(f)

    times = None
    # if forecast for maximum one day (upto 23h) are to be retrieved,
    # collect accumulation data (flux data)
    # with additional days in the beginning and at the end
    # (used for complete disaggregation of original period)
    if c.maxstep < 24:
        day = startm1
        while day < endp1:
                # retrieve MARS data for the whole period
                flexpart = ECFlexpart(c, fluxes=True)
                tmpday = day + datechunk - datetime.timedelta(days=1)
                if tmpday < endp1:
                    dates = day.strftime("%Y%m%d") + "/to/" + \
                            tmpday.strftime("%Y%m%d")
                else:
                    dates = day.strftime("%Y%m%d") + "/to/" + \
                            end.strftime("%Y%m%d")

                print "retrieve " + dates + " in dir " + c.inputdir

                try:
                    flexpart.retrieve(server, dates, times, c.inputdir)
                except IOError:
                    myerror(c,'MARS request failed')

                day += datechunk

    # if forecast data longer than 24h are to be retrieved,
    # collect accumulation data (flux data)
    # with the exact start and end date
    # (disaggregation will be done for the
    # exact time period with boundary conditions)
    else:
        day = start
        while day <= end:
                # retrieve MARS data for the whole period
                flexpart = ECFlexpart(c, fluxes=True)
                tmpday = day + datechunk - datetime.timedelta(days=1)
                if tmpday < end:
                    dates = day.strftime("%Y%m%d") + "/to/" + \
                            tmpday.trftime("%Y%m%d")
                else:
                    dates = day.strftime("%Y%m%d") + "/to/" + \
                            end.strftime("%Y%m%d")

                print "retrieve " + dates + " in dir " + c.inputdir

                try:
                    flexpart.retrieve(server, dates, times, c.inputdir)
                except IOError:
                    myerror(c, 'MARS request failed')

                day += datechunk

    # retrieving of normal data fields (non flux data), (maximum one month)

    # remove old *__* files
    tobecleaned = glob.glob(c.inputdir + '/*__*.' +
                            str(os.getppid()) + '.*.grb')
    for f in tobecleaned:
        os.remove(f)
    day = start
    times = None
    while day <= end:
            # retrieve MARS data for the whole period
            flexpart = ECFlexpart(c, fluxes=False)
            tmpday = day+datechunk-datetime.timedelta(days=1)
            if tmpday < end:
                dates = day.strftime("%Y%m%d") + "/to/" + \
                        tmpday.strftime("%Y%m%d")
            else:
                dates = day.strftime("%Y%m%d") + "/to/" + \
                        end.strftime("%Y%m%d")

            print "retrieve " + dates + " in dir " + c.inputdir

            try:
                flexpart.retrieve(server, dates, times, c.inputdir)
            except IOError:
                myerror(c, 'MARS request failed')

            day += datechunk

    return

if __name__ == "__main__":

    args, c = interpret_args_and_control()
    getMARSdata(args, c)
    normalexit(c)
