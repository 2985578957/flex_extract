#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - moved the getEIdata program into a function "get_mars_data"
#        - moved the AgurmentParser into a seperate function
#        - adatpted the function for the use in flex_extract
#        - renamed file to get_mars_data
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added structured documentation
#        - minor changes in programming style for consistence
#        - added function main and moved function calls vom __main__ there
#          (necessary for better documentation with docstrings for later
#          online documentation)
#        - use of UIFiles class for file selection and deletion
#        - seperated get_mars_data function into several smaller pieces:
#          write_reqheader, mk_server, mk_dates, remove_old, do_retrievment
#
# @License:
#    (C) Copyright 2014-2019.
#    Anne Philipp, Leopold Haimberger
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#*******************************************************************************
'''This script extracts MARS data from ECMWF servers.

At first, the necessary parameters from command line and CONTROL files are
extracted. They define the data set to be extracted from MARS.

This file can also be imported as a module and contains the following
functions:

    * main - the main function of the script
    * get_mars_data - overall control of ECMWF data retrievment
    * write_reqheader - writes the header into the mars_request file
    * mk_server - creates the server connection to ECMWF servers
    * mk_dates - defines the start and end date
    * remove_old - deletes old retrieved grib files
    * do_retrievement - creates individual retrievals

Type: get_mars_data.py --help
to get information about command line parameters.
Read the documentation for usage instructions.
'''
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import sys
import inspect
from datetime import datetime, timedelta

# software specific classes and modules from flex_extract
# add path to local main python path for flex_extract to get full access
sys.path.append(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')
import _config
from Mods.tools import (setup_controldata, my_error, normal_exit, get_cmdline_args,
                   read_ecenv, make_dir)
from Classes.EcFlexpart import EcFlexpart
from Classes.UioFiles import UioFiles
from Classes.MarsRetrieval import MarsRetrieval

try:
    ec_api = True
    import ecmwfapi
except ImportError:
    ec_api = False

try:
    cds_api = True
    import cdsapi
except ImportError:
    cds_api = False
# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''Controls the program to get data out of mars.

    This is done if it is called directly from command line.
    Then it also takes program call arguments and control file input.

    Parameters
    ----------

    Return
    ------

    '''

    c, _, _, _ = setup_controldata()
    get_mars_data(c)
    normal_exit('Retrieving MARS data: Done!')

    return

def get_mars_data(c):
    '''Retrieves the EC data needed for a FLEXPART simulation.

    Start and end dates for retrieval period is set. Retrievals
    are divided into smaller periods if necessary and datechunk parameter
    is set.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    c.ec_api = ec_api
    c.cds_api = cds_api

    if not os.path.exists(c.inputdir):
        make_dir(c.inputdir)

    if c.request == 0:
        print("Retrieving EC data!")
    else:
        if c.request == 1:
            print("Printing mars requests!")
        elif c.request == 2:
            print("Retrieving EC data and printing mars request!")
        write_reqheader(os.path.join(c.inputdir, _config.FILE_MARS_REQUESTS))

    print("start date %s " % (c.start_date))
    print("end date %s " % (c.end_date))

    server = mk_server(c)

    # if data are to be retrieved, clean up any old grib files
    if c.request == 0 or c.request == 2:
        remove_old('*grb', c.inputdir)

    # --------------  flux data ------------------------------------------------
    start, end, datechunk = mk_dates(c, fluxes=True)
    do_retrievement(c, server, start, end, datechunk, fluxes=True)

    # --------------  non flux data --------------------------------------------
    start, end, datechunk = mk_dates(c, fluxes=False)
    do_retrievement(c, server, start, end, datechunk, fluxes=False)

    return

def write_reqheader(marsfile):
    '''Writes header with column names into mars request file.

    Parameters
    ----------
    marsfile : str
        Path to the mars request file.

    Return
    ------

    '''
    MR = MarsRetrieval(None, None)
    attrs = vars(MR).copy()
    del attrs['server']
    del attrs['public']
    with open(marsfile, 'w') as f:
        f.write('request_number' + ', ')
        f.write(', '.join(str(key) for key in sorted(attrs.keys())))
        f.write('\n')

    return

def mk_server(c):
    '''Creates a server connection with available python API.

    Which API is used depends on availability and the dataset to be retrieved.
    The CDS API is used for ERA5 dataset no matter if the user is a member or
    a public user. ECMWF WebAPI is used for all other available datasets.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------
    server : ECMWFDataServer, ECMWFService or Client
        Connection to ECMWF server via python interface ECMWF WebAPI or CDS API.

    '''
    if cds_api and (c.marsclass.upper() == 'EA'):
        server = cdsapi.Client()
        c.ec_api = False
    elif c.ec_api:
        if c.public:
            server = ecmwfapi.ECMWFDataServer()
        else:
            server = ecmwfapi.ECMWFService("mars")
        c.cds_api = False
    else:
        server = False

    print('Using ECMWF WebAPI: ' + str(c.ec_api))
    print('Using CDS API: ' + str(c.cds_api))

    return server


def check_dates_for_nonflux_fc_times(types, times):
    '''
    '''
    for ty, ti in zip(types,times):
        if ty.upper() == 'FC' and int(ti) == 18:
            return True
    return False


def mk_dates(c, fluxes):
    '''Prepares start and end date depending on flux or non flux data.

    If forecast for maximum one day (upto 24h) are to be retrieved, then
    collect accumulation data (flux data) with additional days in the
    beginning and at the end (used for complete disaggregation of
    original period)

    If forecast data longer than 24h are to be retrieved, then
    collect accumulation data (flux data) with the exact start and end date
    (disaggregation will be done for the exact time period with
    boundary conditions)

    Since for basetime the extraction contains the 12 hours upfront,
    if basetime is 0, the starting date has to be the day before and

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    fluxes : boolean, optional
        Decides if the flux parameter settings are stored or
        the rest of the parameter list.
        Default value is False.

    Return
    ------
    start : datetime
        The start date of the retrieving data set.

    end : datetime
        The end date of the retrieving data set.

    chunk : datetime
        Time period in days for one single mars retrieval.

    '''
    start = datetime.strptime(c.start_date, '%Y%m%d')
    end = datetime.strptime(c.end_date, '%Y%m%d')
    chunk = timedelta(days=int(c.date_chunk))

    if c.basetime == 0:
        start = start - timedelta(days=1)

    if c.purefc and fluxes and c.maxstep < 24:
        start = start - timedelta(days=1)
        end = end + timedelta(days=1)

    if not c.purefc and fluxes and not c.basetime == 0:
        start = start - timedelta(days=1)
        end = end + timedelta(days=1)

    # if we have non-flux forecast data starting at 18 UTC
    # we need to start retrieving data one day in advance
    if not fluxes and check_dates_for_nonflux_fc_times(c.type, c.time):
        start = start - timedelta(days=1)

    return start, end, chunk

def remove_old(pattern, inputdir):
    '''Deletes old retrieval files from current input directory
    matching the pattern.

    Parameters
    ----------
    pattern : str
        The sub string pattern which identifies the files to be deleted.

    inputdir : str, optional
        Path to the directory where the retrieved data is stored.

    Return
    ------

    '''
    print('... removing old content of ' + inputdir)

    tobecleaned = UioFiles(inputdir, pattern)
    tobecleaned.delete_files()

    return


def do_retrievement(c, server, start, end, delta_t, fluxes=False):
    '''Divides the complete retrieval period in smaller chunks and
    retrieves the data from MARS.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    server : ECMWFService or ECMWFDataServer
            The server connection to ECMWF.

    start : datetime
        The start date of the retrieval.

    end : datetime
        The end date of the retrieval.

    delta_t : datetime
        Delta_t + 1 is the maximal time period of a single
        retrieval.

    fluxes : boolean, optional
        Decides if the flux parameters are to be retrieved or
        the rest of the parameter list.
        Default value is False.

    Return
    ------

    '''

    # since actual day also counts as one day,
    # we only need to add datechunk - 1 days to retrieval
    # for a period
    delta_t_m1 = delta_t - timedelta(days=1)

    day = start
    while day <= end:
        flexpart = EcFlexpart(c, fluxes)
        tmpday = day + delta_t_m1
        if tmpday < end:
            dates = day.strftime("%Y%m%d") + "/to/" + \
                    tmpday.strftime("%Y%m%d")
        else:
            dates = day.strftime("%Y%m%d") + "/to/" + \
                    end.strftime("%Y%m%d")

        print("... retrieve " + dates + " in dir " + c.inputdir)

        try:
            flexpart.retrieve(server, dates, c.public, c.request, c.inputdir)
        except IOError:
            my_error('MARS request failed')

        day += delta_t

    return

if __name__ == "__main__":
    main()
