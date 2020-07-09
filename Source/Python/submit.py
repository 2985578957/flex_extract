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
#        - job submission on ecgate and cca
#        - job templates suitable for twice daily operational dissemination
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - minor changes in programming style (for consistence)
#        - changed path names to variables from config file
#        - added option for writing mars requests to extra file
#          additionally, as option without submitting the mars jobs
#        - splitted submit function to use genshi templates for the
#          job script and avoid code duplication
#    June 2020 - Anne Philipp
#        - changed finale job_file to filename from config file
#          instead of generating from the template filename
#
# @License:
#    (C) Copyright 2014-2020.
#    Anne Philipp, Leopold Haimberger
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#*******************************************************************************
'''This script allows the user to extract meteorological fields from the ECMWF.

It prepares the settings for retrieving the data from ECMWF servers and
process the resulting files to prepare them for the use with FLEXPART or
FLEXTRA.

If it is supposed to work locally then it works through the necessary
functions get_mars_data and prepare_flexpart. Otherwise it prepares
a job script (korn shell) which will do the necessary work on the
ECMWF server. This script will de submitted via the ecaccess command
ecaccess-job-submit.

This file can also be imported as a module which then contains the following
functions:

    * main - the main function of the script
    * submit - calls mk_jobscript depending on operation mode and submits its
    * mk_jobscript - creates the job script from a template

Type: submit.py --help
to get information about command line parameters.
Read the documentation for usage instructions.
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import sys
from datetime import datetime, timedelta

# software specific classes and modules from flex_extract
import _config
from Mods.tools import (setup_controldata, normal_exit,
                        submit_job_to_ecserver)
from Mods.get_mars_data import get_mars_data
from Mods.prepare_flexpart import prepare_flexpart

# ------------------------------------------------------------------------------
# METHODS
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

    c, ppid, queue, job_template = setup_controldata()

    # on local side
    # starting from an ECMWF server this would also be the local side
    called_from_dir = os.getcwd()
    if queue is None:
        if c.inputdir[0] != '/':
            c.inputdir = os.path.join(called_from_dir, c.inputdir)
        if c.outputdir[0] != '/':
            c.outputdir = os.path.join(called_from_dir, c.outputdir)
        get_mars_data(c)
        if c.request == 0 or c.request == 2:
            prepare_flexpart(ppid, c)
            exit_message = 'FLEX_EXTRACT IS DONE!'
        else:
            exit_message = 'PRINTING MARS_REQUESTS DONE!'
    # send files to ECMWF server
    else:
        submit(job_template, c, queue)
        exit_message = 'FLEX_EXTRACT JOB SCRIPT IS SUBMITED!'

    normal_exit(exit_message)

    return

def submit(jtemplate, c, queue):
    '''Prepares the job script and submits it to the specified queue.

    Parameters
    ----------
    jtemplate : str
        Job template file from sub-directory "_templates" for
        submission to ECMWF. It contains all necessary
        module and variable settings for the ECMWF environment as well as
        the job call and mail report instructions.
        Default is _config.TEMPFILE_JOB.

    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    queue : str
        Name of queue for submission to ECMWF (e.g. ecgate or cca )

    Return
    ------

    '''

    if not c.oper:
    # --------- create on demand job script ------------------------------------
        if c.purefc:
            print('---- Pure forecast mode! ----')
        else:
            print('---- On-demand mode! ----')

        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                _config.FILE_JOB_OD)

        # divide time periode into specified number of job chunks
        # to have multiple job scripts
        if c.job_chunk:
            start = datetime.strptime(c.start_date, '%Y%m%d')
            end = datetime.strptime(c.end_date, '%Y%m%d')
            chunk = timedelta(days=c.job_chunk)
            oneday = timedelta(days=1)

            while start <= end:
                if (start + chunk) <= end:
                    c.end_date = (start + chunk - oneday).strftime("%Y%m%d")
                else:
                    c.end_date = end.strftime("%Y%m%d")

                clist = c.to_list()
                mk_jobscript(jtemplate, job_file, clist)

                job_id = submit_job_to_ecserver(queue, job_file)
                print('The job id is: ' + str(job_id.strip()))

                start = start + chunk
                c.start_date = start.strftime("%Y%m%d")
        # submit a single job script
        else:
            clist = c.to_list()

            mk_jobscript(jtemplate, job_file, clist)

            job_id = submit_job_to_ecserver(queue, job_file)
            print('The job id is: ' + str(job_id.strip()))

    else:
    # --------- create operational job script ----------------------------------
        print('---- Operational mode! ----')

        job_file = os.path.join(_config.PATH_JOBSCRIPTS,
                                _config.FILE_JOB_OP)

        c.start_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.end_date = '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        c.basetime = '${MSJ_BASETIME}'
        if c.maxstep > 24:
            c.time = '${MSJ_BASETIME} {MSJ_BASETIME}'

        clist = c.to_list()

        mk_jobscript(jtemplate, job_file, clist)

        job_id = submit_job_to_ecserver(queue, job_file)
        print('The job id is: ' + str(job_id.strip()))

    print('You should get an email per job with subject flex.hostname.pid')

    return

def mk_jobscript(jtemplate, job_file, clist):
    '''Creates the job script from template.

    Parameters
    ----------
    jtemplate : str
        Job template file from sub-directory "Templates" for
        submission to ECMWF. It contains all necessary
        module and variable settings for the ECMWF environment as well as
        the job call and mail report instructions.
        Default is _config.TEMPFILE_JOB.

    job_file : str
        Path to the job script file.

    clist : list of str
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
