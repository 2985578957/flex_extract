#!/usr/bin/env python
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# Functionality provided: Prepare input 3D-wind fields in hybrid coordinates + surface fields for FLEXPART runs
#
# Creation: October  2014 - Anne Fouilloux - University of Oslo
# Extension November 2015 - Leopold Haimberger - University of Vienna for:
# - using the WebAPI also for general MARS retrievals
# - job submission on ecgate and cca
# - job templates suitable for twice daily operational dissemination
# - dividing retrievals of longer periods into digestable chunks
# - retrieve also longer term forecasts, not only analyses and short term forecast data
# - conversion into GRIB2
# - conversion into .fp format for faster execution of FLEXPART
#
# Further documentation may be obtained from www.flexpart.eu
#
# Requirements:
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)
#
#
import calendar
import shutil
import datetime
import time
import os,sys,glob
import subprocess
import inspect
# add path to submit.py to pythonpath so that python finds its buddies
localpythonpath=os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(localpythonpath)
from UIOTools import UIOFiles
from string import strip
from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
from GribTools import GribTools
from FlexpartTools import EIFlexpart, Control, interpret_args_and_control, normalexit,myerror
from getMARSdata import getMARSdata
from prepareFLEXPART import prepareFLEXPART



def main():

    calledfromdir=os.getcwd()
#    os.chdir(localpythonpath)
    args,c=interpret_args_and_control()
    if args.queue==None:
        if c.inputdir[0]!='/':
            c.inputdir=os.path.join(calledfromdir,c.inputdir)
        if c.outputdir[0]!='/':
            c.outputdir=os.path.join(calledfromdir,c.outputdir)
        getMARSdata(args,c)
	if c.request == 0 or c.request == 2:
            prepareFLEXPART(args,c)
            normalexit(c)
        else:
            normalexit(c)
    else:
        submit(args.job_template,c,args.queue)


def submit(jtemplate,c,queue):

    f=open(jtemplate)
    lftext=f.read().split('\n')
    insert_point=lftext.index('EOF')
    f.close()

    clist=c.tolist()
    colist=[]
    mt=0
    for elem in clist:
        if 'maxstep' in elem:
            mt=int(elem.split(' ')[1])

    for elem in clist:
        if 'start_date' in elem:
            elem='start_date '+'${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'end_date' in elem:
            elem='start_date '+'${MSJ_YEAR}${MSJ_MONTH}${MSJ_DAY}'
        if 'base_time' in elem:
            elem='base_time '+'${MSJ_BASETIME}'
        if 'time' in elem and mt>24:
            elem='time '+'${MSJ_BASETIME} {MSJ_BASETIME}'
        colist.append(elem)

    lftextondemand=lftext[:insert_point]+clist+lftext[insert_point+2:]
    lftextoper=lftext[:insert_point]+colist+lftext[insert_point+2:]

    h=open('job.ksh','w')
    h.write('\n'.join(lftextondemand))
    h.close()

    h=open('joboper.ksh','w')
    h.write('\n'.join(lftextoper))
    h.close()

    try:
        p=subprocess.check_call(['ecaccess-job-submit','-queueName',queue,'job.ksh'])
    except:
        print 'ecaccess-job-submit failed, probably eccert has expired'
        exit(1)
    #pout=p.communicate(input=s)[0]
    print 'You should get an email with subject flex.hostname.pid'




if __name__ == "__main__":
    main()
