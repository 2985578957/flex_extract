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
    '''Get the arguments from script call and from CONTROL file.
    Decides from the argument "queue" if the local version
    is done "queue=None" or the gateway version with "queue=ecgate"
    or "queue=cca".

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
            exit_message = 'FLEX_EXTRACT IS DONE!'
        else:
            exit_message = 'PRINTING MARS_REQUESTS DONE!'
    # send files to ECMWF server
    else:
        submit(args.job_template, c, args.queue)
        exit_message = 'FLEX_EXTRACT JOB SCRIPT IS SUBMITED!'

    normal_exit(exit_message)

    return

def submit(jtemplate, c, queue):
    '''Prepares the job script and submit it to the specified queue.

    Parameters
    ----------
    jtemplate : :obj:`string`
        Job template file from sub-directory "_templates" for
        submission to ECMWF. It contains all necessary
        module and variable settings for the ECMWF environment as well as
        the job call and mail report instructions.
        Default is "job.temp".

    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    queue : :obj:`string`
        Name of queue for submission to ECMWF (e.g. ecgate or cca )

    Return
    ------

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

        job_id = submit_job_to_ecserver(queue, job_file)

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

        job_id = submit_job_to_ecserver(queue, job_file)

    # --------------------------------------------------------------------------
    print('The job id is: ' + str(job_id.strip()))
    print('You should get an email with subject flex.hostname.pid')

    return

if __name__ == "__main__":
    main()
