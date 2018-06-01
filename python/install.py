#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# ToDo AP
# - create a class Installation and divide installation in 3 subdefs for
#   ecgate, local and cca seperatly
# - Change History ist nicht angepasst ans File! Original geben lassen
#************************************************************************
#*******************************************************************************
# @Author: Leopold Haimberger (University of Vienna)
#
# @Date: November 2015
#
# @Change History:
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - moved install_args_and_control in here
#
# @License:
#    (C) Copyright 2015-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Program Functionality:
#    Depending on the selected installation environment (locally or on the
#    ECMWF server ecgate or cca) the program extracts the commandline
#    arguments and the CONTROL file parameter and prepares the corresponding
#    environment. The necessary files are collected in a tar-ball and placed
#    at the target location. There its untared, the environment variables will
#    be set and the Fortran code will be compiled. If the ECMWF environment is
#    selected a job script is prepared and submitted for the remaining
#    configurations after putting the tar-ball to the target ECMWF server.
#
# @Program Content:
#    - main
#    - install_args_and_control
#    - install_via_gateway
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import glob
import subprocess
import inspect
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# software specific classes and modules from flex_extract
from ControlFile import ControlFile

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
        Controls the installation process. Calls the installation function
        if target is specified.

    @Intput:
        <nothing>

    @Return:
        <nothing>
    '''

    os.chdir(LOCAL_PYTHON_PATH)
    args, c = install_args_and_control()

    if args.install_target is not None:
        install_via_gateway(c, args.install_target)
    else:
        print 'Please specify installation target (local|ecgate|cca)'
        print 'use -h or --help for help'

    sys.exit()

    return


def install_args_and_control():
    '''
    @Description:
        Assigns the command line arguments for installation and reads
        CONTROL file content. Apply default values for non mentioned arguments.

    @Input:
        <nothing>

    @Return:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.

        c: instance of class ControlFile
            Contains all necessary information of a CONTROL file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR
            For more information about format and content of the parameter see
            documentation.
    '''
    parser = ArgumentParser(description='Install ECMWFDATA software locally or \
                            on ECMWF machines',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--target', dest='install_target',
                        help="Valid targets: local | ecgate | cca , \
                        the latter two are at ECMWF")
    parser.add_argument("--makefile", dest="makefile",
                        help='Name of Makefile to use for compiling CONVERT2')
    parser.add_argument("--ecuid", dest="ecuid",
                        help='user id at ECMWF')
    parser.add_argument("--ecgid", dest="ecgid",
                        help='group id at ECMWF')
    parser.add_argument("--gateway", dest="gateway",
                        help='name of local gateway server')
    parser.add_argument("--destination", dest="destination",
                        help='ecaccess destination, e.g. leo@genericSftp')

    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        help="FLEXPART root directory on ECMWF servers \
                        (to find grib2flexpart and COMMAND file)\n\
                        Normally ECMWFDATA resides in the scripts directory \
                        of the FLEXPART distribution, thus the:")

# arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        default="job.temp.o",
                        help="job template file for submission to ECMWF")

    parser.add_argument("--controlfile", dest="controlfile",
                        default='CONTROL.temp',
                        help="file with CONTROL parameters")

    args = parser.parse_args()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        print 'Could not read CONTROL file "' + args.controlfile + '"'
        print 'Either it does not exist or its syntax is wrong.'
        print 'Try "' + sys.argv[0].split('/')[-1] + \
              ' -h" to print usage information'
        exit(1)

    if args.install_target != 'local':
        if args.ecgid is None or args.ecuid is None or args.gateway is None \
           or args.destination is None:
            print 'Please enter your ECMWF user id and group id as well as \
                   the \nname of the local gateway and the ectrans \
                   destination '
            print 'with command line options --ecuid --ecgid \
                   --gateway --destination'
            print 'Try "' + sys.argv[0].split('/')[-1] + \
                  ' -h" to print usage information'
            print 'Please consult ecaccess documentation or ECMWF user support \
                   for further details'
            sys.exit(1)
        else:
            c.ecuid = args.ecuid
            c.ecgid = args.ecgid
            c.gateway = args.gateway
            c.destination = args.destination

    if args.makefile:
        c.makefile = args.makefile

    if args.install_target == 'local':
        if args.flexpart_root_scripts is None:
            c.flexpart_root_scripts = '../'
        else:
            c.flexpart_root_scripts = args.flexpart_root_scripts

    if args.install_target != 'local':
        if args.flexpart_root_scripts is None:
            c.ec_flexpart_root_scripts = '${HOME}'
        else:
            c.ec_flexpart_root_scripts = args.flexpart_root_scripts

    return args, c


def install_via_gateway(c, target):
    '''
    @Description:
        Perform the actual installation on local machine or prepare data
        transfer to remote gate and submit a job script which will
        install everything on the remote gate.

    @Input:
        c: instance of class ControlFile
            Contains all necessary information of a CONTROL file. The parameters
            are: DAY1, DAY2, DTIME, MAXSTEP, TYPE, TIME, STEP, CLASS, STREAM,
            NUMBER, EXPVER, GRID, LEFT, LOWER, UPPER, RIGHT, LEVEL, LEVELIST,
            RESOL, GAUSS, ACCURACY, OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA,
            SMOOTH, FORMAT, ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS,
            ECFSDIR, MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR
            For more information about format and content of the parameter see
            documentation.

        target: string
            The target where the installation should be processed.
            E.g. "local", "ecgate" or "cca"

    @Return:
        <nothing>
    '''
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
                    data = 'export FLEXPART_ROOT_SCRIPTS=$HOME'
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
                data += c.ec_flexpart_root_scripts + '/ECMWFDATA7.1/python'
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
            print 'Warning: FLEXPART_ROOT_SCRIPTS has not been specified'
            print 'Only CONVERT2 will be compiled in ' + ecd + '/../src'
        else:
            c.flexpart_root_scripts = os.path.expandvars(os.path.expanduser(
                c.flexpart_root_scripts))
            if os.path.abspath(ecd) != os.path.abspath(c.flexpart_root_scripts):
                os.chdir('/')
                p = subprocess.check_call(['tar', '-cvf',
                                           ecd + '../ECMWFDATA7.1.tar',
                                           ecd + 'python',
                                           ecd + 'grib_templates',
                                           ecd + 'src'])
                try:
                    os.makedirs(c.flexpart_root_scripts + '/ECMWFDATA7.1')
                finally:
                    pass
                os.chdir(c.flexpart_root_scripts + '/ECMWFDATA7.1')
                p = subprocess.check_call(['tar', '-xvf',
                                           ecd + '../ECMWFDATA7.1.tar'])
                os.chdir(c.flexpart_root_scripts + '/ECMWFDATA7.1/src')

        os.chdir('../src')
        print(('install ECMWFDATA7.1 software on ' + target + ' in directory '
               + os.getcwd()))
        if c.makefile is None:
            makefile = 'Makefile.local.ifort'
        else:
            makefile = c.makefile
        flist = glob.glob('*.mod') + glob.glob('*.o')
        if flist:
            p = subprocess.check_call(['rm'] + flist)
        try:
            print 'Using makefile: ' + makefile
            p = subprocess.check_call(['make', '-f', makefile])
            p = subprocess.check_call(['ls', '-l', 'CONVERT2'])
        except subprocess.CalledProcessError as e:
            print 'compile failed with the following error:'
            print e.output
            print 'please edit ' + makefile + \
                  ' or try another Makefile in the src directory.'
            print 'most likely GRIB_API_INCLUDE_DIR, GRIB_API_LIB  \
                   and EMOSLIB must be adapted.'
            print 'Available Makefiles:'
            print glob.glob('Makefile*')
    elif target.lower() == 'ecgate':
        os.chdir('/')
        p = subprocess.check_call(['tar', '-cvf',
                                   ecd + '../ECMWFDATA7.1.tar',
                                   ecd + 'python',
                                   ecd + 'grib_templates',
                                   ecd + 'src'])
        try:
            p = subprocess.check_call(['ecaccess-file-put',
                                       ecd + '../ECMWFDATA7.1.tar',
                                       'ecgate:/home/ms/' + c.ecgid + '/' +
                                       c.ecuid + '/ECMWFDATA7.1.tar'])
        except subprocess.CalledProcessError as e:
            print 'ecaccess-file-put failed! \
                   Probably the eccert key has expired.'
            exit(1)

        try:
            p = subprocess.check_call(['ecaccess-job-submit',
                                       '-queueName',
                                       target,
                                       ecd + 'python/compilejob.ksh'])
            print 'compilejob.ksh has been submitted to ecgate for  \
                   installation in ' + c.ec_flexpart_root_scripts + \
                   '/ECMWFDATA7.1'
            print 'You should get an email with subject flexcompile within  \
                   the next few minutes'
        except subprocess.CalledProcessError as e:
            print 'ecaccess-job-submit failed!'
            exit(1)

    elif target.lower() == 'cca':
        os.chdir('/')
        p = subprocess.check_call(['tar', '-cvf',
                                   ecd + '../ECMWFDATA7.1.tar',
                                   ecd + 'python',
                                   ecd + 'grib_templates',
                                   ecd + 'src'])
        try:
            p = subprocess.check_call(['ecaccess-file-put',
                                       ecd + '../ECMWFDATA7.1.tar',
                                       'cca:/home/ms/' + c.ecgid + '/' +
                                       c.ecuid + '/ECMWFDATA7.1.tar'])
        except subprocess.CalledProcessError as e:
            print 'ecaccess-file-put failed! \
                   Probably the eccert key has expired.'
            exit(1)

        try:
            p = subprocess.check_call(['ecaccess-job-submit',
                                       '-queueName',
                                       target,
                                       ecd + 'python/compilejob.ksh'])
            print 'compilejob.ksh has been submitted to cca for installation in ' +\
                  c.ec_flexpart_root_scripts + '/ECMWFDATA7.1'
            print 'You should get an email with subject flexcompile \
                   within the next few minutes'
        except subprocess.CalledProcessError as e:
            print 'ecaccess-job-submit failed!'
            exit(1)

    else:
        print 'ERROR: unknown installation target ', target
        print 'Valid targets: ecgate, cca, local'

    return


if __name__ == "__main__":
    main()
