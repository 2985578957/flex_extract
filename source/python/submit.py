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
#        - job submission on ecgate and cca
#        - job templates suitable for twice daily operational dissemination
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - minor changes in programming style (for consistence)
#        - changed path names to variables from config file
#        - added option for writing mars requests to extra file
#          additionally,as option without submitting the mars jobs
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program Functionality:
#    This program is the main program of flex_extract and controls the
#    program flow.
#    If it is supposed to work locally then it works through the necessary
#    functions get_mars_data and prepareFlexpart. Otherwise it prepares
#    a shell job script which will do the necessary work on the
#    ECMWF server and is submitted via ecaccess-job-submit.
#
# @Program Content:
#    - main
#    - submit
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import subprocess
import inspect
import collections

# software specific classes and modules from flex_extract
import _config
from mods.tools import (normal_exit, get_cmdline_arguments,
                        submit_job_to_ecserver, read_ecenv)
from mods.get_mars_data import get_mars_data
from mods.prepare_flexpart import prepare_flexpart
from classes.ControlFile import ControlFile

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

def main():
    '''
    @Description:
        Get the arguments from script call and from CONTROL file.
        Decides from the argument "queue" if the local version
        is done "queue=None" or the gateway version with "queue=ecgate"
        or "queue=cca".

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''

    args = get_cmdline_arguments()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        print('Could not read CONTROL file "' + args.controlfile + '"')
        print('Either it does not exist or its syntax is wrong.')
        print('Try "' + sys.argv[0].split('/')[-1] + \
              ' -h" to print usage information')
        sys.exit(1)

    env_parameter = read_ecenv(_config.PATH_ECMWF_ENV)
    c.assign_args_to_control(args)
    c.assign_envs_to_control(env_parameter)
    c.check_conditions(args.queue)

    # on local side
    # on ECMWF server this would also be the local side
    called_from_dir = os.getcwd()
    if args.queue is None:
        if c.inputdir[0] != '/':
            c.inputdir = os.path.join(called_from_dir, c.inputdir)
        if c.outputdir[0] != '/':
            c.outputdir = os.path.join(called_from_dir, c.outputdir)
        get_mars_data(c)
        if c.request == 0 or c.request == 2:
            prepare_flexpart(args.ppid, c)
            normal_exit(c.mailfail, 'FLEX_EXTRACT IS DONE!')
        else:
            normal_exit(c.mailfail, 'PRINTING MARS_REQUESTS DONE!')
    # send files to ECMWF server and install there
    else:
        submit(args.job_template, c, args.queue)

    return

def submit(jtemplate, c, queue):
    '''
    @Description:
        Prepares the job script and submit it to the specified queue.

    @Input:
        jtemplate: string
            Job template file from sub-directory "_templates" for
            submission to ECMWF. It contains all necessary
            module and variable settings for the ECMWF environment as well as
            the job call and mail report instructions.
            Default is "job.temp".

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

        queue: string
            Name of queue for submission to ECMWF (e.g. ecgate or cca )

    @Return:
        <nothing>
    '''

    # read template file and get index for CONTROL input
    with open(os.path.join(_config.PATH_TEMPLATES, jtemplate)) as f:
        lftext = f.read().split('\n')
    insert_point = lftext.index('EOF')

    if not c.basetime:
    # --------- create on demand job script ------------------------------------
        if c.maxstep > 24:
            print('---- Pure forecast mode! ----')
        else:
            print('---- On-demand mode! ----')
        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                jtemplate[:-4] + 'ksh')
        clist = c.to_list()

        lftextondemand = lftext[:insert_point] + clist + lftext[insert_point:]

        with open(job_file, 'w') as f:
            f.write('\n'.join(lftextondemand))

        submit_job_to_ecserver(queue, job_file)

    else:
    # --------- create operational job script ----------------------------------
        print('---- Operational mode! ----')
        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                jtemplate[:-5] + 'oper.ksh')

        if c.maxstep:
            mt = int(c.maxstep)
        else:
            mt = 0

        c.start_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.end_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.base_time = '${MSJ_BASETIME}'
        if mt > 24:
            c.time = '${MSJ_BASETIME} {MSJ_BASETIME}'

        colist = c.to_list()

        lftextoper = lftext[:insert_point] + colist + lftext[insert_point + 2:]

        with open(job_file, 'w') as f:
            f.write('\n'.join(lftextoper))

        submit_job_to_ecserver(queue, job_file)

    # --------------------------------------------------------------------------
    print('You should get an email with subject flex.hostname.pid')

    return

if __name__ == "__main__":
    main()
