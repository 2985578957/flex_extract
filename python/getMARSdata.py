#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
# - add function docstrings!!!!
#************************************************************************
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - moved the getEIdata program into a function "getMARSdata"
#        - moved the AgurmentParser into a seperate function
#        - adatpted the function for the use in flex_extract
#        - renamed file to getMARSdata
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added structured documentation
#        - minor changes in programming style for consistence
#        - added function main and moved function calls vom __main__ there
#          (necessary for better documentation with docstrings for later
#          online documentation)
#        - use of UIFiles class for file selection and deletion

#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program Functionality:
#    This program can be used as a module in the whole flex_extract process
#    or can be run by itself to just extract MARS data from ECMWF. To do so,
#    a couple of necessary parameters has to be passed with the program call.
#    See documentation for more details.
#
# @Program Content:
#    - main
#    - getMARSdata
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import datetime
import inspect
try:
    ecapi=True
    import ecmwfapi
except ImportError:
    ecapi=False

# add path to pythonpath so that python finds its buddies
localpythonpath = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)

# software specific classes and modules from flex_extract
from ControlFile import ControlFile
from Tools import myerror, normalexit, \
                          interpret_args_and_control
from ECFlexpart import ECFlexpart
from UIOFiles import UIOFiles

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''
    @Description:
        If getMARSdata is called from command line, this function controls
        the program flow and calls the argumentparser function and
        the getMARSdata function for retrieving EC data.

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''
    args, c = interpret_args_and_control()
    getMARSdata(args, c)
    normalexit(c)

    return

def getMARSdata(args, c):
    '''
    @Description:
        Retrieves the EC data needed for a FLEXPART simulation.
        Start and end dates for retrieval period is set. Retrievals
        are divided into smaller periods if necessary and datechunk parameter
        is set.

    @Input:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

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

    if not os.path.exists(c.inputdir):
        os.makedirs(c.inputdir)

    print("Retrieving EC data!")
    print("start date %s " % (c.start_date))
    print("end date %s " % (c.end_date))

    if ecapi:
        server = ecmwfapi.ECMWFService("mars")
    else:
        server = False

    c.ecapi = ecapi
    print 'ecapi: ', c.ecapi

    # set start date of retrieval period
    start = datetime.date(year=int(c.start_date[:4]),
                          month=int(c.start_date[4:6]),
                          day=int(c.start_date[6:]))
    startm1 = start - datetime.timedelta(days=1)
    if c.basetime == '00':
        start = startm1

    # set end date of retrieval period
    end = datetime.date(year=int(c.end_date[:4]),
                        month=int(c.end_date[4:6]),
                        day=int(c.end_date[6:]))
    if c.basetime == '00' or c.basetime == '12':
        endp1 = end + datetime.timedelta(days=1)
    else:
        endp1 = end + datetime.timedelta(days=2)

    # set time period of one single retrieval
    datechunk = datetime.timedelta(days=int(c.date_chunk))

    # --------------  flux data ------------------------------------------------
    print 'removing old flux content of ' + c.inputdir
    tobecleaned = UIOFiles('*_acc_*.' + str(os.getppid()) + '.*.grb')
    tobecleaned.listFiles(c.inputdir)
    tobecleaned.deleteFiles()

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
                flexpart.retrieve(server, dates, c.inputdir)
            except IOError:
                myerror(c, 'MARS request failed')

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
                flexpart.retrieve(server, dates, c.inputdir)
            except IOError:
                myerror(c, 'MARS request failed')

            day += datechunk

    # --------------  non flux data --------------------------------------------
    print 'removing old non flux content of ' + c.inputdir
    tobecleaned = UIOFiles('*__*.' + str(os.getppid()) + '.*.grb')
    tobecleaned.listFiles(c.inputdir)
    tobecleaned.deleteFiles()

    day = start
    while day <= end:
            # retrieve all non flux MARS data for the whole period
            flexpart = ECFlexpart(c, fluxes=False)
            tmpday = day + datechunk - datetime.timedelta(days=1)
            if tmpday < end:
                dates = day.strftime("%Y%m%d") + "/to/" + \
                        tmpday.strftime("%Y%m%d")
            else:
                dates = day.strftime("%Y%m%d") + "/to/" + \
                        end.strftime("%Y%m%d")

            print "retrieve " + dates + " in dir " + c.inputdir

            try:
                flexpart.retrieve(server, dates, c.inputdir)
            except IOError:
                myerror(c, 'MARS request failed')

            day += datechunk

    return

if __name__ == "__main__":
    main()

