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

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import inspect
from datetime import datetime, timedelta

# software specific classes and modules from flex_extract
sys.path.append('../')
import _config
from tools import (my_error, normal_exit, get_cmdline_arguments,
                   read_ecenv, make_dir)
from classes.EcFlexpart import EcFlexpart
from classes.UioFiles import UioFiles

try:
    ecapi = True
    import ecmwfapi
except ImportError:
    ecapi = False
# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''
    @Description:
        If get_mars_data is called directly from command line,

        the program flow and calls the argumentparser function and
        the get_mars_data function for retrieving EC data.

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''

    args = get_cmdline_arguments()
    c = ControlFile(args.controlfile)

    env_parameter = read_ecenv(_config.PATH_ECMWF_ENV)
    c.assign_args_to_control(args)
    c.assign_envs_to_control(env_parameter)
    c.check_conditions(args.queue)

    get_mars_data(c)
    normal_exit(c.mailfail, 'Done!')

    return

def get_mars_data(c):
    '''
    @Description:
        Retrieves the EC data needed for a FLEXPART simulation.
        Start and end dates for retrieval period is set. Retrievals
        are divided into smaller periods if necessary and datechunk parameter
        is set.

    @Input:
        c: instance of class ControlFile
            Contains all the parameters of CONTROL file and
            command line.
            For more information about format and content of the parameter
            see documentation.

    @Return:
        <nothing>
    '''

    if not os.path.exists(c.inputdir):
        make_dir(c.inputdir)

    if c.request == 0 or c.request == 2:
        print("Retrieving EC data!")
    elif c.request == 1:
        print("Printing mars requests!")

    print("start date %s " % (c.start_date))
    print("end date %s " % (c.end_date))

    if ecapi:
        if c.public:
            server = ecmwfapi.ECMWFDataServer()
        else:
            server = ecmwfapi.ECMWFService("mars")
    else:
        server = False

    c.ecapi = ecapi
    print('Using ECMWF WebAPI: ' + str(c.ecapi))

    # basetime geht rückwärts

    # if basetime 00
    # dann wird von 12 am vortag bis 00 am start tag geholt
    # aber ohne 12 selbst sondern 12 + step

    # if basetime 12
    # dann wird von 00 + step bis 12 am start tag geholt

    # purer forecast wird vorwärts bestimmt.
    # purer forecast mode ist dann wenn  größer 24 stunden
    # wie kann das noch festgestellt werden ????
    # nur FC und steps mehr als 24 ?
    # die einzige problematik beim reinen forecast ist die benennung der files!
    # also sobald es Tagesüberschneidungen gibt
    # allerdings ist das relevant und ersichtlich an den NICHT FLUSS DATEN

    start = datetime.strptime(c.start_date, '%Y%m%d')
    end = datetime.strptime(c.end_date, '%Y%m%d')
    # time period for one single retrieval
    datechunk = timedelta(days=int(c.date_chunk))

    if c.basetime == '00':
        start = start - timedelta(days=1)

    if c.maxstep <= 24:
        startm1 = start - timedelta(days=1)

    if c.basetime == '00' or c.basetime == '12':
        # endp1 = end + timedelta(days=1)
        endp1 = end
    else:
        # endp1 = end + timedelta(days=2)
        endp1 = end + timedelta(days=1)

    # --------------  flux data ------------------------------------------------
    if c.request == 0 or c.request == 2:
        print('... removing old flux content of ' + c.inputdir)
        tobecleaned = UioFiles(c.inputdir,
                               '*_acc_*.' + str(os.getppid()) + '.*.grb')
        tobecleaned.delete_files()

    # if forecast for maximum one day (upto 24h) are to be retrieved,
    # collect accumulation data (flux data)
    # with additional days in the beginning and at the end
    # (used for complete disaggregation of original period)
    if c.maxstep <= 24:
        do_retrievement(c, server, startm1, endp1, datechunk, fluxes=True)

    # if forecast data longer than 24h are to be retrieved,
    # collect accumulation data (flux data)
    # with the exact start and end date
    # (disaggregation will be done for the
    # exact time period with boundary conditions)
    else:
        do_retrievement(c, server, start, end, datechunk, fluxes=True)

    # --------------  non flux data --------------------------------------------
    if c.request == 0 or c.request == 2:
        print('... removing old non flux content of ' + c.inputdir)
        tobecleaned = UioFiles(c.inputdir,
                               '*__*.' + str(os.getppid()) + '.*.grb')
        tobecleaned.delete_files()

    do_retrievement(c, server, start, end, datechunk, fluxes=False)

    return

def do_retrievement(c, server, start, end, delta_t, fluxes=False):
    '''
    @Description:
        Divides the complete retrieval period in smaller chunks and
        retrieves the data from MARS.

    @Input:
        c: instance of class ControlFile
            Contains all the parameters of CONTROL file and
            command line.
            For more information about format and content of the parameter
            see documentation.

        server: instance of ECMWFService
            The server connection to ECMWF

        start: instance of datetime
            The start date of the retrieval.

        end: instance of datetime
            The end date of the retrieval.

        delta_t: instance of datetime
            Delta_t +1 is the maximal time period of a single
            retrieval.

        fluxes: boolean, optional
            Decides if the flux parameters are to be retrieved or
            the rest of the parameter list.
            Default value is False.

    @Return:
        <nothing>
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
