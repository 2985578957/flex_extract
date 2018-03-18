#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - Change History ist nicht angepasst ans File! Original geben lassen
# - dead code ? what to do?
# - seperate operational and reanlysis for clarification
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: October 2014

@ChangeHistory:
    November 2015 - Leopold Haimberger (University of Vienna):
        - using the WebAPI also for general MARS retrievals
        - job submission on ecgate and cca
        - job templates suitable for twice daily operational dissemination
        - dividing retrievals of longer periods into digestable chunks
        - retrieve also longer term forecasts, not only analyses and
          short term forecast data
        - conversion into GRIB2
        - conversion into .fp format for faster execution of FLEXPART

    February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - minor changes in programming style for consistence

@License:
    (C) Copyright 2014 UIO.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    - A standard python 2.6 or 2.7 installation
    - dateutils
    - matplotlib (optional, for debugging)
    - ECMWF specific packages, all available from https://software.ecmwf.int/
        ECMWF WebMARS, gribAPI with python enabled, emoslib and
        ecaccess web toolkit

@Description:
    Further documentation may be obtained from www.flexpart.eu.

    Functionality provided:
        Prepare input 3D-wind fields in hybrid coordinates +
        surface fields for FLEXPART runs
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import calendar
import shutil
import datetime
import time
import os, sys, glob
import subprocess
import inspect
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(localpythonpath)
from UIOTools import UIOFiles
from string import strip
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from GribTools import GribTools
from FlexpartTools import ECFlexpart, Control, interpret_args_and_control, normalexit, myerror
from getMARSdata import getMARSdata
from prepareFLEXPART import prepareFLEXPART
# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
def main():
    '''
    @Description:
        Get the arguments from script call and initialize an object from
        Control class. Decides from the argument "queue" if the local version
        is done "queue=None" or the gateway version "queue=ecgate".

    @Input:
        <nothing>

    @Return:
        <nothing>
    '''
    calledfromdir = os.getcwd()
    args, c = interpret_args_and_control()
    if args.queue is None:
        if c.inputdir[0] != '/':
            c.inputdir = os.path.join(calledfromdir, c.inputdir)
        if c.outputdir[0] != '/':
            c.outputdir = os.path.join(calledfromdir, c.outputdir)
        getMARSdata(args, c)
        prepareFLEXPART(args, c)
        normalexit(c)
    else:
        submit(args.job_template, c, args.queue)

    return

def submit(jtemplate, c, queue):
    #AP divide in two submits , ondemand und operational
    '''
    @Description:
        Prepares the job script and submit it to the specified queue.

    @Input:
        jtemplate: string
            Job template file for submission to ECMWF. It contains all necessary
            module and variable settings for the ECMWF environment as well as
            the job call and mail report instructions.
            Default is "job.temp".

        c: instance of class Control
            Contains all the parameters of control files, which are e.g.:
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
#AP es gibt mehrere EOFs überprüfen!

    # put all parameters of control instance into a list
    clist = c.tolist()  # reanalysis (EI)
    colist = []  # operational
    mt = 0

#AP wieso 2 for loops?
#AP dieser part ist für die CTBTO Operational retrieves bis zum aktuellen Tag.
    for elem in clist:
        if 'maxstep' in elem:
            mt = int(elem.split(' ')[1])

    for elem in clist:
        if 'start_date' in elem:
            elem = 'start_date ' + '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'end_date' in elem:
#AP Fehler?! Muss end_date heissen
            elem = 'start_date ' + '${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'base_time' in elem:
            elem = 'base_time ' + '${MSJ_BASETIME}'
        if 'time' in elem and mt > 24:
            elem = 'time ' + '${MSJ_BASETIME} {MSJ_BASETIME}'
        colist.append(elem)
#AP end

#AP whats the difference between clist and colist ?! What is MSJ?

    lftextondemand = lftext[:insert_point] + clist + lftext[insert_point + 2:]
    lftextoper = lftext[:insert_point] + colist + lftext[insert_point + 2:]

    with open('job.ksh', 'w') as h:
        h.write('\n'.join(lftextondemand))

#AP this is not used ?! what is it for?
#maybe a differentiation is needed
    h = open('joboper.ksh', 'w')
    h.write('\n'.join(lftextoper))
    h.close()
#AP end

    # submit job script to queue
    try:
        p = subprocess.check_call(['ecaccess-job-submit', '-queueName',
                                   queue,' job.ksh'])
    except:
        print('ecaccess-job-submit failed, probably eccert has expired')
        exit(1)

    print('You should get an email with subject flex.hostname.pid')

    return

if __name__ == "__main__":
    main()
