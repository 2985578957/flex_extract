#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - Functionality Provided is not correct for this file
# - localpythonpath should not be set in module load section!
# - create a class Installation and divide installation in 3 subdefs for
#   ecgate, local and cca seperatly
# - Change History ist nicht angepasst ans File! Original geben lassen
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
from FlexpartTools import EIFlexpart, Control, install_args_and_control
from getMARSdata import getMARSdata
from prepareFLEXPART import prepareFLEXPART

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
def main():
    '''
    '''
    os.chdir(localpythonpath)
    args, c = install_args_and_control()
    if args.install_target is not None:
        install_via_gateway(c, args.install_target)
    else:
        print('Please specify installation target (local|ecgate|cca)')
        print('use -h or --help for help')
    sys.exit()

def install_via_gateway(c, target):

    ecd = c.ecmwfdatadir
    template = ecd + 'python/compilejob.temp'
    job = ecd + 'python/compilejob.ksh'
    fo = open(job, 'w')
#AP could do with open(template) as f, open(job, 'w') as fo:
#AP or nested with statements
    with open(template) as f:
        fdata = f.read().split('\n')
        for data in fdata:
            if 'MAKEFILE=' in data:
                if c.makefile is not None:
                    data = 'export MAKEFILE=' + c.makefile
            if 'FLEXPART_ROOT_SCRIPTS=' in data:
                if c.flexpart_root_scripts != '../':
                    data = 'export FLEXPART_ROOT_SCRIPTS=' + \
                            c.flexpart_root_scripts
                else:
                    data='export FLEXPART_ROOT_SCRIPTS=$HOME'
            if target.lower() != 'local':
                if '--workdir' in data:
                    data = '#SBATCH --workdir=/scratch/ms/' + c.ecgid + \
                            '/' + c.ecuid
                if '##PBS -o' in data:
                    data = '##PBS -o /scratch/ms/' + c.ecgid + '/' + c.ecuid + \
                            'flex_ecmwf.$Jobname.$Job_ID.out'
                if 'FLEXPART_ROOT_SCRIPTS=' in data:
                    if c.ec_flexpart_root_scripts != '../':
                        data = 'export FLEXPART_ROOT_SCRIPTS=' + \
                                c.ec_flexpart_root_scripts
                    else:
                        data = 'export FLEXPART_ROOT_SCRIPTS=$HOME'
            fo.write(data + '\n')
    f.close()
    fo.close()

    if target.lower() != 'local':
        template = ecd + 'python/job.temp.o'
#AP hier eventuell Zeile für Zeile lesen und dann if Entscheidung
        with open(template) as f:
            fdata = f.read().split('\n')
        f.close()
        fo = open(template[:-2], 'w')
        for data in fdata:
            if '--workdir' in data:
                data = '#SBATCH --workdir=/scratch/ms/' + c.ecgid + \
                        '/' + c.ecuid
            if '##PBS -o' in data:
                data = '##PBS -o /scratch/ms/' + c.ecgid + '/' + \
                        c.ecuid + 'flex_ecmwf.$Jobname.$Job_ID.out'
            if  'export PATH=${PATH}:' in data:
                data += c.ec_flexpart_root_scripts + '/ECMWFDATA7.0/python'
            if 'cat>>' in data or 'cat >>' in data:
                i = data.index('>')
                fo.write(data[:i] + data[i+1:] + '\n')
                fo.write('GATEWAY ' + c.gateway + '\n')
                fo.write('DESTINATION ' + c.destination + '\n')
                fo.write('EOF\n')

            fo.write(data + '\n')
        fo.close()

        job = ecd + 'python/ECMWF_ENV'
        with open(job, 'w') as fo:
            fo.write('ECUID ' + c.ecuid + '\n')
            fo.write('ECGID ' + c.ecgid + '\n')
            fo.write('GATEWAY ' + c.gateway + '\n')
            fo.write('DESTINATION ' + c.destination + '\n')
        fo.close()



    if target.lower() == 'local':
        # compile CONVERT2
        if c.flexpart_root_scripts is None or c.flexpart_root_scripts == '../':
            print('Warning: FLEXPART_ROOT_SCRIPTS has not been specified')
            print('Only CONVERT2 will be compiled in ' + ecd + '/../src')
        else:
            c.flexpart_root_scripts = os.path.expandvars(os.path.expanduser(
                                        c.flexpart_root_scripts))
            if os.path.abspath(ecd) != os.path.abspath(c.flexpart_root_scripts):
                os.chdir('/')
                p = subprocess.check_call(['tar', '-cvf',
                                           ecd + '../ECMWFDATA7.0.tar',
                                           ecd + 'python',
                                           ecd + 'grib_templates',
                                           ecd + 'src'])
                try:
                    os.makedirs(c.flexpart_root_scripts + '/ECMWFDATA7.0')
                except:
                    pass
                os.chdir(c.flexpart_root_scripts + '/ECMWFDATA7.0')
                p = subprocess.check_call(['tar', '-xvf',
                                           ecd + '../ECMWFDATA7.0.tar'])
                os.chdir(c.flexpart_root_scripts + '/ECMWFDATA7.0/src')

        os.chdir('../src')
        print(('install ECMWFDATA7.0 software on ' + target + ' in directory '
               + os.getcwd()))
        if c.makefile is None:
            makefile = 'Makefile.local.ifort'
        else:
            makefile = c.makefile
        flist = glob.glob('*.mod') + glob.glob('*.o')
        if flist:
            p = subprocess.check_call(['rm'] + flist)
        try:
            print(('Using makefile: ' + makefile))
            p = subprocess.check_call(['make', '-f', makefile])
            p = subprocess.check_call(['ls', '-l',' CONVERT2'])
        except:
            print('compile failed - please edit ' + makefile +
                  ' or try another Makefile in the src directory.')
            print('most likely GRIB_API_INCLUDE_DIR, GRIB_API_LIB \
                    and EMOSLIB must be adapted.')
            print('Available Makefiles:')
            print(glob.glob('Makefile*'))

    elif target.lower() == 'ecgate':
        os.chdir('/')
        p = subprocess.check_call(['tar', '-cvf',
                                   ecd + '../ECMWFDATA7.0.tar',
                                   ecd + 'python',
                                   ecd + 'grib_templates',
                                   ecd + 'src'])
        try:
            p = subprocess.check_call(['ecaccess-file-put',
                                       ecd + '../ECMWFDATA7.0.tar',
                                       'ecgate:/scratch/ms/' + c.ecgid + '/' +
                                       c.ecuid + '/ECMWFDATA7.0.tar'])
        except:
            print('ecaccess-file-put failed! Probably the eccert key has expired.')
            exit(1)
        p = subprocess.check_call(['ecaccess-job-submit',
                                   '-queueName',
                                   target,
                                   ecd + 'python/compilejob.ksh'])
        print('compilejob.ksh has been submitted to ecgate for \
                installation in ' + c.ec_flexpart_root_scripts +
                '/ECMWFDATA7.0')
        print('You should get an email with subject flexcompile within \
                the next few minutes')

    elif target.lower() == 'cca':
        os.chdir('/')
        p = subprocess.check_call(['tar', '-cvf',
                                   ecd + '../ECMWFDATA7.0.tar',
                                   ecd + 'python',
                                   ecd + 'grib_templates',
                                   ecd + 'src'])
        try:
            p = subprocess.check_call(['ecaccess-file-put',
                                       ecd + '../ECMWFDATA7.0.tar',
                                       'cca:/scratch/ms/' + c.ecgid + '/' +
                                       c.ecuid + '/ECMWFDATA7.0.tar'])
        except:
            print('ecaccess-file-put failed! \
                    Probably the eccert key has expired.')
            exit(1)

        p=subprocess.check_call(['ecaccess-job-submit',
                                '-queueName',
                                target,
                                ecd + 'python/compilejob.ksh']))
        print('compilejob.ksh has been submitted to cca for installation in ' +
              c.ec_flexpart_root_scripts + '/ECMWFDATA7.0')
        print('You should get an email with subject flexcompile \
                within the next few minutes')

    else:
        print('ERROR: unknown installation target ', target)
        print('Valid targets: ecgate, cca, local')

    return


if __name__ == "__main__":
    main()
