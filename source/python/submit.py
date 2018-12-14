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
from mods.tools import (normal_exit, get_cmdline_args,
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

    args = get_cmdline_args()
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
    '''Prepares the job script and submits it to the specified queue.

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

    if not c.basetime:
    # --------- create on demand job script ------------------------------------
        if c.purefc:
            print('---- Pure forecast mode! ----')
        else:
            print('---- On-demand mode! ----')

        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                jtemplate[:-5] + '.ksh')

        clist = c.to_list()

        mk_jobscript(jtemplate, job_file, clist)

    else:
    # --------- create operational job script ----------------------------------
        print('---- Operational mode! ----')

        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                jtemplate[:-5] + 'oper.ksh')

        c.start_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.end_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.base_time = '${MSJ_BASETIME}'
        if c.maxstep > 24:
            c.time = '${MSJ_BASETIME} {MSJ_BASETIME}'

        clist = c.to_list()

        mk_jobscript(jtemplate, job_file, clist)

    # --------- submit the job_script to the ECMWF server
    job_id = submit_job_to_ecserver(queue, job_file)
    print('The job id is: ' + str(job_id.strip()))
    print('You should get an email with subject flex.hostname.pid')

    return

def mk_jobscript(jtemplate, job_file, clist):
    '''Creates the job script from template.

    Parameters
    ----------
    jtemplate : :obj:`string`
        Job template file from sub-directory "_templates" for
        submission to ECMWF. It contains all necessary
        module and variable settings for the ECMWF environment as well as
        the job call and mail report instructions.
        Default is "job.temp".

    job_file : :obj:`string`
        Path to the job script file.

    clist : :obj:`list` of :obj:`string`
        Contains all necessary parameters for ECMWF CONTROL file.

    Return
    ------

    '''
    from genshi.template.text import NewTextTemplate
    from genshi.template import  TemplateLoader
    from genshi.template.eval import UndefinedError

    # load template and insert control content as list
    try:
        loader = TemplateLoader(_config.PATH_TEMPLATES, auto_reload=False)
        control_template = loader.load(jtemplate,
                                       cls=NewTextTemplate)

        stream = control_template.generate(control_content=clist)
    except UndefinedError as e:
        print('... ERROR ' + str(e))

        sys.exit('\n... error occured while trying to generate jobscript')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to generate jobscript')

    # create jobscript file
    try:
        with open(job_file, 'w') as f:
            f.write(stream.render('text'))
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to write ' + job_file)

    return

if __name__ == "__main__":
    main()
