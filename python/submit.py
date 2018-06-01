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

# software specific classes and modules from flex_extract
from tools import interpret_args_and_control, normal_exit
from get_mars_data import get_mars_data
from prepare_flexpart import prepare_flexpart

# add path to pythonpath so that python finds its buddies
LOCAL_PYTHON_PATH = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if LOCAL_PYTHON_PATH not in sys.path:
    sys.path.append(LOCAL_PYTHON_PATH)

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

    called_from_dir = os.getcwd()
    args, c = interpret_args_and_control()

    # on local side
    if args.queue is None:
        if c.inputdir[0] != '/':
            c.inputdir = os.path.join(called_from_dir, c.inputdir)
        if c.outputdir[0] != '/':
            c.outputdir = os.path.join(called_from_dir, c.outputdir)
        get_mars_data(args, c)
        prepare_flexpart(args, c)
        normal_exit(c)
    # on ECMWF server
    else:
        submit(args.job_template, c, args.queue)

    return

def submit(jtemplate, c, queue):
    '''
    @Description:
        Prepares the job script and submit it to the specified queue.

    @Input:
        jtemplate: string
            Job template file for submission to ECMWF. It contains all necessary
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

    # read template file and split from newline signs
    with open(jtemplate) as f:
        lftext = f.read().split('\n')
        insert_point = lftext.index('EOF')

    # put all parameters of ControlFile instance into a list
    clist = c.to_list() # ondemand
    colist = []  # operational
    mt = 0

    for elem in clist:
        if 'maxstep' in elem:
            mt = int(elem.split(' ')[1])

    for elem in clist:
        if 'start_date' in elem:
            elem = 'start_date ' + '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'end_date' in elem:
            elem = 'end_date ' + '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'base_time' in elem:
            elem = 'base_time ' + '${MSJ_BASETIME}'
        if 'time' in elem and mt > 24:
            elem = 'time ' + '${MSJ_BASETIME} {MSJ_BASETIME}'
        colist.append(elem)

    lftextondemand = lftext[:insert_point] + clist + lftext[insert_point + 2:]
    lftextoper = lftext[:insert_point] + colist + lftext[insert_point + 2:]

    with open('job.ksh', 'w') as h:
        h.write('\n'.join(lftextondemand))

    with open('joboper.ksh', 'w') as h:
        h.write('\n'.join(lftextoper))

    # submit job script to queue
    try:
        p = subprocess.check_call(['ecaccess-job-submit', '-queueName',
                                   queue, 'job.ksh'])
    except subprocess.CalledProcessError as e:
        print 'ecaccess-job-submit failed!'
        print 'Error Message: '
        print e.output
        exit(1)

    print 'You should get an email with subject flex.hostname.pid'

    return

if __name__ == "__main__":
    main()
