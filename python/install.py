#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#    - get_install_cmdline_arguments
#    - install_via_gateway
#    - mk_tarball
#    - mk_env_vars
#    - mk_compilejob
#    - mk_job_template
#    - delete_convert_build
#    - make_convert_build
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import sys
import subprocess
import inspect
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# software specific classes and modules from flex_extract
from ControlFile import ControlFile
from UioFiles import UioFiles
from tools import make_dir, put_file_to_ecserver, submit_job_to_ecserver

# add path to pythonpath so that python finds its buddies
LOCAL_PYTHON_PATH = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
if LOCAL_PYTHON_PATH not in sys.path:
    sys.path.append(LOCAL_PYTHON_PATH)

_VERSION_STR = '7.1'

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
    args = get_install_cmdline_arguments()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        print 'Could not read CONTROL file "' + args.controlfile + '"'
        print 'Either it does not exist or its syntax is wrong.'
        print 'Try "' + sys.argv[0].split('/')[-1] + \
              ' -h" to print usage information'
        exit(1)

    c.assign_args_to_control(args)
    c.check_install_conditions()

    install_via_gateway(c)

    return

def get_install_cmdline_arguments():
    '''
    @Description:
        Decomposes the command line arguments and assigns them to variables.
        Apply default values for non mentioned arguments.

    @Input:
        <nothing>

    @Return:
        args: instance of ArgumentParser
            Contains the commandline arguments from script/program call.
    '''
    parser = ArgumentParser(description='Install flex_extract software locally or \
                            on ECMWF machines',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--target', dest='install_target', default=None,
                        help="Valid targets: local | ecgate | cca , \
                        the latter two are at ECMWF")
    parser.add_argument("--makefile", dest="makefile", default=None,
                        help='Name of Makefile to use for compiling CONVERT2')
    parser.add_argument("--ecuid", dest="ecuid", default=None,
                        help='user id at ECMWF')
    parser.add_argument("--ecgid", dest="ecgid", default=None,
                        help='group id at ECMWF')
    parser.add_argument("--gateway", dest="gateway", default=None,
                        help='name of local gateway server')
    parser.add_argument("--destination", dest="destination", default=None,
                        help='ecaccess destination, e.g. leo@genericSftp')

    parser.add_argument("--flexpart_root_scripts", dest="flexpart_root_scripts",
                        default=None, help="FLEXPART root directory on ECMWF \
                        servers (to find grib2flexpart and COMMAND file)\n\
                        Normally flex_extract resides in the scripts directory \
                        of the FLEXPART distribution, thus the:")

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        default="job.temp.o",
                        help="job template file for submission to ECMWF")

    parser.add_argument("--controlfile", dest="controlfile",
                        default='CONTROL.temp',
                        help="file with CONTROL parameters")

    args = parser.parse_args()

    return args


def install_via_gateway(c):
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

    @Return:
        <nothing>
    '''

    ecd = c.ecmwfdatadir
    tarball_name = 'flex_extract_v' + _VERSION_STR + '.tar'
    target_dir = 'flex_extract_v' + _VERSION_STR
    fortran_executable = 'CONVERT2'

    if c.install_target.lower() != 'local':

        mk_compilejob(ecd + 'python/compilejob.temp', c.makefile,
                      c.install_target, c.ecuid, c.ecgid,
                      c.flexpart_root_scripts)

        mk_job_template(ecd + 'python/job.temp.o', c.ecuid, c.ecgid, c.gateway,
                        c.destination, c.flexpart_root_scripts)

        mk_env_vars(ecd, c.ecuid, c.ecgid, c.gateway, c.destination)

        #os.chdir('/')

        mk_tarball(ecd, tarball_name)

        put_file_to_ecserver(ecd, tarball_name, c.install_target,
                             c.ecuid, c.ecgid)

        result_code = submit_job_to_ecserver(ecd + '/python/', c.install_target,
                                             'compilejob.ksh')

        print 'job compilation script has been submitted to ecgate for ' + \
              'installation in ' + c.flexpart_root_scripts + \
               '/' + target_dir
        print 'You should get an email with subject flexcompile within ' + \
              'the next few minutes!'

    else: #local
        if not c.flexpart_root_scripts or c.flexpart_root_scripts == '../':
            print 'WARNING: FLEXPART_ROOT_SCRIPTS has not been specified'
            print 'There will be only the compilation of ' + \
                  ' in ' + ecd + '/src'
            os.chdir(ecd + '/src')
        else: # creates the target working directory for flex_extract
            c.flexpart_root_scripts = os.path.expandvars(os.path.expanduser(
                c.flexpart_root_scripts))
            if os.path.abspath(ecd) != os.path.abspath(c.flexpart_root_scripts):
                os.chdir('/')
                mk_tarball(ecd, tarball_name)
                make_dir(c.flexpart_root_scripts + '/' + target_dir)
                os.chdir(c.flexpart_root_scripts + '/' + target_dir)
                print 'Untar ...'
                subprocess.check_call(['tar', '-xvf',
                                       ecd + '../' + tarball_name])
                os.chdir(c.flexpart_root_scripts + '/' + target_dir + '/src')

        # Create Fortran executable - CONVERT2
        print 'Install ' + target_dir + ' software on ' + \
              c.install_target + ' in directory ' + \
              os.path.abspath(os.getcwd() + '/../') + '\n'

        delete_convert_build('')
        make_convert_build('', c.makefile, fortran_executable)

    return

def mk_tarball(ecd, tarname):
    '''
    @Description:
        Creates a tarball from all files which need to be sent to the
        installation directory.
        It does not matter if this is local or remote.
        Collects all python files, the Fortran source and makefiles,
        the ECMWF_ENV file, the CONTROL files as well as
        the korn shell and template files.

    @Input:
        ecd: string
            The path were the file is to be stored.

        tarname: string
            The name of the file to send to the ECMWF server.

    @Return:
        <nothing>
    '''

    print 'Create tarball ...'
    try:
        subprocess.check_call(['tar -cvf '+
                               ecd + '../' + tarname + ' ' +
                               ecd + 'python/*py ' +
                               ecd + 'python/CONTROL* ' +
                               ecd + 'python/*ksh ' +
                               ecd + 'python/*temp* ' +
                               ecd + 'python/ECMWF_ENV ' +
                               ecd + 'grib_templates ' +
                               ecd + 'src/*.f ' +
                               ecd + 'src/*.f90 ' +
                               ecd + 'src/*.h ' +
                               ecd + 'src/Makefile*'], shell=True)
    except subprocess.CalledProcessError as e:
        print 'ERROR:'
        print e.output
        sys.exit('could not make installation tar ball!')

    return

def mk_env_vars(ecd, ecuid, ecgid, gateway, destination):
    '''
    @Description:
        Creates a file named ECMWF_ENV which contains the
        necessary environmental variables at ECMWF servers.

    @Input:
        ecd: string
            The path were the file is to be stored.

        ecuid: string
            The user id on ECMWF server.

        ecgid: string
            The group id on ECMWF server.

        gateway: string
            The gateway server the user is using.

        destination: string
            The remote destination which is used to transfer files
            from ECMWF server to local gateway server.

    @Return:
        <nothing>
    '''

    with open(ecd + 'python/ECMWF_ENV', 'w') as fo:
        fo.write('ECUID ' + ecuid + '\n')
        fo.write('ECGID ' + ecgid + '\n')
        fo.write('GATEWAY ' + gateway + '\n')
        fo.write('DESTINATION ' + destination + '\n')

    return

def mk_compilejob(template, makefile, target, ecuid, ecgid, fp_root):
    '''
    @Description:
        Modifies the original job template file so that it is specified
        for the user and the environment were it will be applied. Result
        is stored in a new file "job.temp" in the python directory.

    @Input:
        template: string
            File which contains the original text for the job template.
            It must contain the complete path to the file.

        makefile: string
            Name of the makefile which should be used to compile FORTRAN
            CONVERT2 program.

        target: string
            The target where the installation should be done, e.g. the queue.

        ecuid: string
            The user id on ECMWF server.

        ecgid: string
            The group id on ECMWF server.

        fp_root: string
           Path to the root directory of FLEXPART environment or flex_extract
           environment.

    @Return:
        <nothing>
    '''

    with open(template) as f:
        fdata = f.read().split('\n')

    with open(template[:-4] + 'ksh', 'w') as fo:
        for data in fdata:
            if 'MAKEFILE=' in data:
                data = 'export MAKEFILE=' + makefile
            elif 'FLEXPART_ROOT_SCRIPTS=' in data:
                if fp_root != '../':
                    data = 'export FLEXPART_ROOT_SCRIPTS=' + fp_root
                else:
                    data = 'export FLEXPART_ROOT_SCRIPTS=$HOME'
            elif target.lower() != 'local':
                if '--workdir' in data:
                    data = '#SBATCH --workdir=/scratch/ms/' + \
                            ecgid + '/' + ecuid
                elif '##PBS -o' in data:
                    data = '##PBS -o /scratch/ms/' + ecgid + '/' + ecuid + \
                           'flex_ecmwf.$Jobname.$Job_ID.out'
                elif 'FLEXPART_ROOT_SCRIPTS=' in data:
                    if fp_root != '../':
                        data = 'export FLEXPART_ROOT_SCRIPTS=' + fp_root
                    else:
                        data = 'export FLEXPART_ROOT_SCRIPTS=$HOME'
            fo.write(data + '\n')

    return

def mk_job_template(template, ecuid, ecgid, gateway, destination, fp_root):
    '''
    @Description:
        Modifies the original job template file so that it is specified
        for the user and the environment were it will be applied. Result
        is stored in a new file "job.temp" in the python directory.

    @Input:
        template: string
            File which contains the original text for the job template.
            It must contain the complete path to the file.

        ecuid: string
            The user id on ECMWF server.

        ecgid: string
            The group id on ECMWF server.

        gateway: string
            The gateway server the user is using.

        destination: string
            The remote destination which is used to transfer files
            from ECMWF server to local gateway server.

        fp_root: string
           Path to the root directory of FLEXPART environment or flex_extract
           environment.

    @Return:
        <nothing>
    '''

    with open(template) as f:
        fdata = f.read().split('\n')

    with open(template[:-2], 'w') as fo:
        for data in fdata:
            if '--workdir' in data:
                data = '#SBATCH --workdir=/scratch/ms/' + ecgid + \
                        '/' + ecuid
            elif '##PBS -o' in data:
                data = '##PBS -o /scratch/ms/' + ecgid + '/' + \
                        ecuid + 'flex_ecmwf.$Jobname.$Job_ID.out'
            elif  'export PATH=${PATH}:' in data:
                data += fp_root + '/flex_extract_v7.1/python'

            fo.write(data + '\n')
    return

def delete_convert_build(ecd):
    '''
    @Description:
        Clean up the Fortran source directory and remove all
        build files (e.g. *.o, *.mod and CONVERT2)

    @Input:
        ecd: string
            The path to the Fortran program.

    @Return:
        <nothing>
    '''

    modfiles = UioFiles(ecd, '*.mod')
    objfiles = UioFiles(ecd, '*.o')
    exefile = UioFiles(ecd, 'CONVERT2')

    modfiles.delete_files()
    objfiles.delete_files()
    exefile.delete_files()

    return

def make_convert_build(ecd, makefile, f_executable):
    '''
    @Description:
        Compiles the Fortran code and generates the executable.

    @Input:
        ecd: string
            The path were the file is to be stored.

        makefile: string
            The name of the makefile which should be used.

        f_executable: string
            The name of the executable the Fortran program generates after
            compilation.

    @Return:
        <nothing>
    '''

    try:
        print 'Using makefile: ' + makefile
        p = subprocess.Popen(['make', '-f', ecd + makefile],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=1)
        pout, perr = p.communicate()
        print pout
        if p.returncode != 0:
            print perr
            print 'Please edit ' + makefile + \
                  ' or try another Makefile in the src directory.'
            print 'Most likely GRIB_API_INCLUDE_DIR, GRIB_API_LIB ' \
                  'and EMOSLIB must be adapted.'
            print 'Available Makefiles:'
            print UioFiles('.', 'Makefile*')
            sys.exit('Compilation failed!')
    except ValueError as e:
        print 'ERROR: Makefile call failed:'
        print e
    else:
        subprocess.check_call(['ls', '-l', ecd + f_executable])

    return


if __name__ == "__main__":
    main()
