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
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)
#
import calendar
import shutil
import datetime
import time
import os,inspect,sys
import socket
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if localpythonpath not in sys.path:
    sys.path.append(localpythonpath)
from UIOTools import UIOFiles
#from string import strip
from GribTools import GribTools
from FlexpartTools import EIFlexpart, Control,interpret_args_and_control, cleanup
from opposite import opposite

hostname=socket.gethostname()
ecapi= 'ecmwf' not in hostname

try:
    if ecapi:
        import ecmwfapi
except ImportError:
    ecapi=False


def prepareFLEXPART(args,c):



    namelist='fort.4'

    if not args.ppid:
        c.ppid=str(os.getppid())
    else:
        c.ppid=args.ppid

    c.ecapi=ecapi

    syear=int(c.start_date[:4])
    smonth=int(c.start_date[4:6])
    sday=int(c.start_date[6:])
    start = datetime.date( year = syear, month = smonth, day = sday )
    eyear=int(c.end_date[:4])
    emonth=int(c.end_date[4:6])
    eday=int(c.end_date[6:])

    end = datetime.date( year = eyear, month = emonth, day = eday )

    inputfiles=UIOFiles(['.grib', '.grb', '.grib1', '.grib2', '.grb1','.grb2'])

    startm1=start- datetime.timedelta(days=1)
    endp1=end + datetime.timedelta(days=1)

    inputfiles.listFiles(c.inputdir, '*OG_acc_SL*.'+c.ppid+'.*')
    if not os.path.exists(c.outputdir):
        os.makedirs(c.outputdir)

    flexpart = EIFlexpart(c,fluxes=True)
    flexpart.create_namelist(c,'fort.4')
    flexpart.deacc_fluxes(inputfiles, c)

    inputfiles=UIOFiles(['.grib', '.grb', '.grib1', '.grib2', '.grb1','.grb2'])

    print 'Prepare '+start.strftime("%Y%m%d") + "/to/" + end.strftime("%Y%m%d")
    # we will make the list of files from the root inputdir
    inputfiles.listFiles(c.inputdir, '????__??.*'+c.ppid+'.*')

    if c.basetime=='00':
        start=startm1
    flexpart = EIFlexpart(c)
    flexpart.create(inputfiles, c) # produce FLEXPART-ready GRIB files
    flexpart.process_output(c) # process GRIB files - copy/transfer/interpolate them or make them GRIB2

    if int(c.debug)!=0:
        print('Temporary files left intact')
    else:
        cleanup(c)

if __name__ == "__main__":
    args,c=interpret_args_and_control()
    prepareFLEXPART(args,c)


