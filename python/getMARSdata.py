#!/usr/bin/env python
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# Functionality provided: Prepare input 3D-wind fields in hybrid coordinates + surface fields for FLEXPART runs
#
# Creation: October  2014 - Anne Fouilloux - University of Oslo
# Extension November 2015 - Leopold Haimberger - University of Vienna for:
# - using the WebAPI also for general MARS retrievals
# - job submission on ecgate and cca
# - job templates suitable for twice daily operational dissemination
# - dividing retrievals of longer periods into digestable chunks
# - retrieve also longer term forecasts, not only analyses and short term forecast data
# - conversion into GRIB2
# - conversion into .fp format for faster execution of FLEXPART
#
#
# Further documentation may be obtained from www.flexpart.eu
#
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)
#
# Get MARS GRIB fields from ECMWF for FLEXPART
#

#import socket

#hostname=socket.gethostname()
#ecapi= 'ecmwf' not in hostname
try:
    ecapi=True
    import ecmwfapi
except ImportError:
    ecapi=False

import calendar
import shutil
import datetime
import time
import os,glob,sys,inspect
#from string import strip
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)

from FlexpartTools import MARSretrieval, EIFlexpart, silentremove, \
     Control,myerror,normalexit, interpret_args_and_control


def getMARSdata(args,c):

    if not os.path.exists(c.inputdir):
        os.makedirs(c.inputdir)


    if c.request == 0:
        print("Retrieving EC data!")
    else:
        if c.request == 1:
            print("Printing mars requests!")
        elif c.request == 2:
            print("Retrieving EC data and printing mars request!")
        # first, write header with the mars parameter to file
        # create a dummy MarsRetrieval to get parameter
        MR = MARSretrieval(None, None)
        attrs = vars(MR).copy()
        del attrs['server']
        del attrs['public']
        marsfile = os.path.join(c.inputdir, 'mars_requests.csv')
        with open(marsfile, 'w') as f:
            f.write('request_number' + ', ')
            f.write(', '.join(str(key) for key in sorted(attrs.iterkeys())))
            f.write('\n')

    print "start date %s "%(c.start_date)
    print "end date %s "%(c.end_date)

    if ecapi:
        if int(c.public):
            server = ecmwfapi.ECMWFDataServer()
        else:
            server = ecmwfapi.ECMWFService("mars")
    else:
        server = False

    c.ecapi=ecapi
    print 'ecapi:',c.ecapi
# Retrieve ERA interim data for running flexpart

    syear=int(c.start_date[:4])
    smonth=int(c.start_date[4:6])
    sday=int(c.start_date[6:])
    start = datetime.date( year = syear, month = smonth, day = sday )
    startm1=start- datetime.timedelta(days=1)
    if c.basetime=='00':
        start=startm1
    eyear=int(c.end_date[:4])
    emonth=int(c.end_date[4:6])
    eday=int(c.end_date[6:])

    end = datetime.date( year = eyear, month = emonth, day = eday )
    if c.basetime=='00' or c.basetime=='12':
        endp1=end+ datetime.timedelta(days=1)
    else:
        endp1=end+ datetime.timedelta(days=2)

    datechunk=datetime.timedelta(days=int(c.date_chunk))
    if c.request == 0 or c.request == 2:
        print 'removing content of '+c.inputdir
        tobecleaned=glob.glob(c.inputdir+'/*_acc_*.'+str(os.getppid())+'.*.grb')
        for f in tobecleaned:
            os.remove(f)

    times=None
    if c.maxstep<=24:
        day=startm1
        while day<endp1:
            # we need to retrieve MARS data for this period (maximum one month)
            flexpart = EIFlexpart(c,fluxes=True)
            if day+datechunk-datetime.timedelta(days=1)<endp1:
                dates= day.strftime("%Y%m%d") + "/to/" + (day+datechunk-datetime.timedelta(days=1)).strftime("%Y%m%d")
            else:
                dates= day.strftime("%Y%m%d") + "/to/" + end.strftime("%Y%m%d")

            print "retrieve " + dates + " in dir " + c.inputdir
            try:
                flexpart.retrieve(server, c.public, dates, c.request, times, c.inputdir)
            except IOError:
                myerror(c,'MARS request failed')

            day+=datechunk
    else:
        day=start
        while day<=end:
            # we need to retrieve MARS data for this period (maximum one month)
            flexpart = EIFlexpart(c,fluxes=True)
            if day+datechunk-datetime.timedelta(days=1)<end:
                dates= day.strftime("%Y%m%d") + "/to/" + (day+datechunk-datetime.timedelta(days=1)).strftime("%Y%m%d")
            else:
                dates= day.strftime("%Y%m%d") + "/to/" + end.strftime("%Y%m%d")

            print "retrieve " + dates + " in dir " + c.inputdir
            flexpart.retrieve(server, c.public, dates, c.request, times, c.inputdir)
            day+=datechunk


    if c.request == 0 or c.request == 2:
        print 'removing content of '+c.inputdir
        tobecleaned=glob.glob(c.inputdir+'/*__*.'+str(os.getppid())+'.*.grb')
        for f in tobecleaned:
            os.remove(f)

    day=start
    times=None
    while day<=end:

            # we need to retrieve MARS data for this period (maximum one month)
        flexpart = EIFlexpart(c)
        if day+datechunk-datetime.timedelta(days=1)<end:
            dates= day.strftime("%Y%m%d") + "/to/" + (day+datechunk-datetime.timedelta(days=1)).strftime("%Y%m%d")
        else:
            dates= day.strftime("%Y%m%d") + "/to/" + end.strftime("%Y%m%d")
        print "retrieve " + dates + " in dir " + c.inputdir

        flexpart.retrieve(server, c.public, dates, c.request, times, c.inputdir)
        day+=datechunk


if __name__ == "__main__":

    args,c=interpret_args_and_control()
    getMARSdata(args,c)
    normalexit(c)
