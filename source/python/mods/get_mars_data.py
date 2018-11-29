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
#
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
#    - get_mars_data
#    - do_retrievement
#
#*******************************************************************************
"""ToDo: Name of litte program

ToDo: Add desccription

ToDo: Add Conditions

This script requires that `...` be installed within the Python
environment you are running this script in.

This file can also be imported as a module and contains the following
functions:

    * get_mars_data -
    * do_retrievement -
    * main - the main function of the script
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import inspect
from datetime import datetime, timedelta

# software specific classes and modules from flex_extract
sys.path.append(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')
import _config
from tools import (my_error, normal_exit, get_cmdline_arguments,
                   read_ecenv, make_dir)
from classes.EcFlexpart import EcFlexpart
from classes.UioFiles import UioFiles
from classes.MarsRetrieval import MarsRetrieval

try:
    ecapi = True
    import ecmwfapi
except ImportError:
    ecapi = False
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

    args = get_cmdline_arguments()
    c = ControlFile(args.controlfile)

    env_parameter = read_ecenv(_config.PATH_ECMWF_ENV)
    c.assign_args_to_control(args)
    c.assign_envs_to_control(env_parameter)
    c.check_conditions(args.queue)

    get_mars_data(c)
    normal_exit(c.mailops, c.queue, 'Done!')

    return

def get_mars_data(c):
    '''Retrieves the EC data needed for a FLEXPART simulation.

    Start and end dates for retrieval period is set. Retrievals
    are divided into smaller periods if necessary and datechunk parameter
    is set.

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    c.ecapi = ecapi

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
        remove_old('*grb')

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
    marsfile : :obj:`string`
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
        f.write(', '.join(str(key) for key in sorted(attrs.iterkeys())))
        f.write('\n')

    return

def mk_server(c):
    '''Creates server connection if ECMWF WebAPI is available.

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------
    server : :obj:`ECMWFDataServer` or :obj:`ECMWFService`
        Connection to ECMWF server via python interface ECMWF WebAPI.

    '''
    if c.ecapi:
        if c.public:
            server = ecmwfapi.ECMWFDataServer()
        else:
            server = ecmwfapi.ECMWFService("mars")
    else:
        server = False

    print('Using ECMWF WebAPI: ' + str(c.ecapi))

    return server


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
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    fluxes : :obj:`boolean`, optional
        Decides if the flux parameter settings are stored or
        the rest of the parameter list.
        Default value is False.

    Return
    ------
    start : :obj:`datetime`
        The start date of the retrieving data set.

    end : :obj:`datetime`
        The end date of the retrieving data set.

    chunk : :obj:`datetime`
        Time period in days for one single mars retrieval.

    '''
    start = datetime.strptime(c.start_date, '%Y%m%d')
    end = datetime.strptime(c.end_date, '%Y%m%d')
    chunk = timedelta(days=int(c.date_chunk))

    if c.basetime:
        if c.basetime == '00':
            start = start - timedelta(days=1)

    if c.maxstep <= 24 and fluxes:
        start = start - timedelta(days=1)
        end = end + timedelta(days=1)

    return start, end, chunk

def remove_old(pattern):
    '''Deletes old retrieval files matching the pattern.

    Parameters
    ----------
    pattern : :obj:`string`
        The sub string pattern which identifies the files to be deleted.

    Return
    ------

    '''
    print('... removing old content of ' + c.inputdir)

    tobecleaned = UioFiles(c.inputdir, pattern)
    tobecleaned.delete_files()

    return


def do_retrievement(c, server, start, end, delta_t, fluxes=False):
    '''Divides the complete retrieval period in smaller chunks and
    retrieves the data from MARS.

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    server : :obj:`ECMWFService`
            The server connection to ECMWF.

    start : :obj:`datetime`
        The start date of the retrieval.

    end : :obj:`datetime`
        The end date of the retrieval.

    delta_t : :obj:`datetime`
        Delta_t + 1 is the maximal time period of a single
        retrieval.

    fluxes : :obj:`boolean`, optional
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
            my_error(c.mailfail, 'MARS request failed')

        day += delta_t

    return

if __name__ == "__main__":
    main()
