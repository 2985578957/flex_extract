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
#        - BUGFIX: removed call of clean_up-Function after call of
#               prepareFlexpart in main since it is already called in
#               prepareFlexpart at the end!
#        - created function main and moved the two function calls for
#          arguments and prepare_flexpart into it
#
# @License:
#    (C) Copyright 2014-2019.
#    Anne Philipp, Leopold Haimberger
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#*******************************************************************************
'''This script prepares the final version of the grib files which are
then used by FLEXPART.

It converts the bunch of grib files extracted via get_mars_data before,
by doing the necessary conversion to get consistent grids or the
disaggregation of flux data. Finally, the data fields are combined
in files per available hour with the naming convention xxYYMMDDHH,
where xx should be 2 arbitrary letters (mostly xx is chosen to be "EN").

This file can also be imported as a module which then contains the following
functions:

    * main
    * prepare_flexpart

Type: prepare_flexpart.py --help
to get information about command line parameters.
Read the documentation for usage instructions.
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import datetime
import os
import inspect
import sys
import socket

# software specific classes and modules from flex_extract
# add path to local main python path for flex_extract to get full access
sys.path.append(os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe()))) + '/../')
import _config
from checks import check_ppid
from classes.UioFiles import UioFiles
from classes.ControlFile import ControlFile
from tools import clean_up, get_cmdline_args, read_ecenv, make_dir
from classes.EcFlexpart import EcFlexpart

ecapi = 'ecmwf' not in socket.gethostname()
try:
    if ecapi:
        import ecmwfapi
except ImportError:
    ecapi = False

# ------------------------------------------------------------------------------
# FUNCTION
# ------------------------------------------------------------------------------
def main():
    '''Controls the program to prepare flexpart input files from mars data.

    This is done if it is called directly from command line.
    Then it also takes program call arguments and control file input.

    Parameters
    ----------

    Return
    ------

    '''

    args = get_cmdline_args()
    c = ControlFile(args.controlfile)

    env_parameter = read_ecenv(_config.PATH_ECMWF_ENV)
    c.assign_args_to_control(args)
    c.assign_envs_to_control(env_parameter)
    c.check_conditions(args.queue)

    prepare_flexpart(args.ppid, c)

    return

def prepare_flexpart(ppid, c):
    '''Converts the mars data into flexpart ready input files.

    Specific data fields are converted to a different grid and the flux
    data are going to be disaggregated. The data fields are collected by
    hour and stored in a file with a specific FLEXPART relevant naming
    convention.

    Parameters
    ----------
    ppid : int
        Contains the ppid number of the current ECMWF job. It will be None if
        the method was called within this module.

    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    check_ppid(c, ppid)

    c.ecapi = ecapi

    # create the start and end date
    start = datetime.date(year=int(c.start_date[:4]),
                          month=int(c.start_date[4:6]),
                          day=int(c.start_date[6:]))

    end = datetime.date(year=int(c.end_date[:4]),
                        month=int(c.end_date[4:6]),
                        day=int(c.end_date[6:]))

    # if basetime is 00
    # assign starting date minus 1 day
    # since we need the 12 hours upfront
    # (the day before from 12 UTC to current day 00 UTC)
    if c.basetime == 0:
        start = start - datetime.timedelta(days=1)

    print('Prepare ' + start.strftime("%Y%m%d") +
           "/to/" + end.strftime("%Y%m%d"))

    # create output dir if necessary
    if not os.path.exists(c.outputdir):
        make_dir(c.outputdir)

    # get all files with flux data to be deaccumulated
    inputfiles = UioFiles(c.inputdir, '*OG_acc_SL*.' + str(c.ppid) + '.*')

    # deaccumulate the flux data
    flexpart = EcFlexpart(c, fluxes=True)
    flexpart.write_namelist(c)
    flexpart.deacc_fluxes(inputfiles, c)

    # get a list of all other files
    inputfiles = UioFiles(c.inputdir, '????__??.*' + str(c.ppid) + '.*')

    # produce FLEXPART-ready GRIB files and process them -
    # copy/transfer/interpolate them or make them GRIB2
    flexpart = EcFlexpart(c, fluxes=False)
    flexpart.create(inputfiles, c)
    if c.stream.lower() == 'elda':
        flexpart.calc_extra_elda(os.path.join(c.inputdir, c.prefix))
    flexpart.process_output(c)

    # make use of a possible conversion to a
    # specific flexpart binary format
    if c.grib2flexpart:
        flexpart.prepare_fp_files(c)

    # check if in debugging mode, then store all files
    # otherwise delete temporary files
    if c.debug:
        print('\nTemporary files left intact')
    else:
        clean_up(c)

    return

if __name__ == "__main__":
    main()
