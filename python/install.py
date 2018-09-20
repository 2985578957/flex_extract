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
#        - splitted code in smaller functions
#        - delete convert build files in here instead of compile job script
#        - changed static path names to Variables from config file
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
#    - un_tarball
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
import glob
import subprocess
import inspect
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# software specific classes and modules from flex_extract
import _config
from ControlFile import ControlFile
from UioFiles import UioFiles
from tools import make_dir, put_file_to_ecserver, submit_job_to_ecserver

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

    #os.chdir(_config.PATH_LOCAL_PYTHON)

    args = get_install_cmdline_arguments()

    try:
        c = ControlFile(args.controlfile)
    except IOError:
        print('Could not read CONTROL file "' + args.controlfile + '"')
        print('Either it does not exist or its syntax is wrong.')
        print('Try "' + sys.argv[0].split('/')[-1] +
              ' -h" to print usage information')
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
                        of the FLEXPART distribution.")

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
    import tarfile

    ecd = _config.PATH_FLEXEXTRACT_DIR
    tarball_name = _config.FLEXEXTRACT_DIRNAME + '.tar'
    tar_file = os.path.join(ecd, tarball_name)

    target_dirname = _config.FLEXEXTRACT_DIRNAME
    fortran_executable = _config.FORTRAN_EXECUTABLE

    if c.install_target.lower() != 'local': # ecgate or cca

        mk_compilejob(c.makefile, c.install_target, c.ecuid, c.ecgid,
                      c.flexpart_root_scripts)

        mk_job_template(c.ecuid, c.ecgid, c.gateway,
                        c.destination, c.flexpart_root_scripts)

        mk_env_vars(c.ecuid, c.ecgid, c.gateway, c.destination)

        mk_tarball(tar_file)

        put_file_to_ecserver(ecd, tarball_name, c.install_target,
                             c.ecuid, c.ecgid)

        submit_job_to_ecserver(c.install_target,
                               os.path.join(_config.PATH_RELATIVE_JOBSCRIPTS,
                                            _config.FILE_INSTALL_COMPILEJOB))

        print('job compilation script has been submitted to ecgate for ' +
              'installation in ' + c.flexpart_root_scripts +
               '/' + target_dirname)
        print('You should get an email with subject "flexcompile" within ' +
              'the next few minutes!')

    else: #local
        if c.flexpart_root_scripts == _config.PATH_FLEXEXTRACT_DIR :
            print('WARNING: FLEXPART_ROOT_SCRIPTS has not been specified')
            print('flex_extract will be installed in here by compiling the ' +
                  'Fortran source in ' + _config.PATH_FORTRAN_SRC)
            os.chdir(_config.PATH_FORTRAN_SRC)
        else: # creates the target working directory for flex_extract
            c.flexpart_root_scripts = os.path.expandvars(os.path.expanduser(
                                        c.flexpart_root_scripts))
            if os.path.abspath(ecd) != os.path.abspath(c.flexpart_root_scripts):
                mk_tarball(tar_file)
                make_dir(os.path.join(c.flexpart_root_scripts,
                                      target_dirname))
                os.chdir(os.path.join(c.flexpart_root_scripts,
                                      target_dirname))
                un_tarball(tar_file)
                os.chdir(os.path.join(c.flexpart_root_scripts,
                                      target_dirname,
                                      _config.PATH_RELATIVE_FORTRAN_SRC))

        # Create Fortran executable - CONVERT2
        print('Install ' + target_dirname + ' software at ' +
              c.install_target + ' in directory ' +
              os.path.abspath(c.flexpart_root_scripts) + '\n')

        delete_convert_build('.')
        make_convert_build('.', c.makefile)

        os.chdir(ecd)
        if os.path.isfile(tar_file):
            os.remove(tar_file)

    return

def mk_tarball(tarball_path):
    '''
    @Description:
        Creates a tarball with all necessary files which need to be sent to the
        installation directory.
        It does not matter if this is local or remote.
        Collects all python files, the Fortran source and makefiles,
        the ECMWF_ENV file, the CONTROL files as well as the
        template files.

    @Input:
        tarball_path: string
            The complete path to the tar file which will contain all
            relevant data for flex_extract.

    @Return:
        <nothing>
    '''
    import tarfile
    from glob import glob

    print('Create tarball ...')

    # change to FLEXEXTRACT directory so that the tar can contain
    # relative pathes to the files and directories
    ecd = _config.PATH_FLEXEXTRACT_DIR + '/'
    os.chdir(ecd)

    # get lists of the files to be added to the tar file
    ECMWF_ENV_FILE = [_config.PATH_RELATIVE_ECMWF_ENV]
    pyfiles = [os.path.relpath(x, ecd)
               for x in glob(_config.PATH_LOCAL_PYTHON +
                             os.path.sep + '*py')]
    controlfiles = [os.path.relpath(x, ecd)
                    for x in glob(_config.PATH_CONTROLFILES +
                                  os.path.sep + 'CONTROL*')]
    tempfiles = [os.path.relpath(x, ecd)
                 for x in glob(_config.PATH_TEMPLATES +
                               os.path.sep + '*')]
    ffiles = [os.path.relpath(x, ecd)
              for x in glob(_config.PATH_FORTRAN_SRC +
                            os.path.sep + '*.f*')]
    hfiles = [os.path.relpath(x, ecd)
              for x in glob(_config.PATH_FORTRAN_SRC +
                            os.path.sep + '*.h')]
    makefiles = [os.path.relpath(x, ecd)
                 for x in glob(_config.PATH_FORTRAN_SRC +
                               os.path.sep + 'Makefile*')]

    # concatenate single lists to one for a better looping
    filelist = pyfiles + controlfiles + tempfiles + ffiles + hfiles + \
               makefiles + ECMWF_ENV_FILE

    # create installation tar-file
    try:
        with tarfile.open(tarball_path, "w:gz") as tar_handle:
            for file in filelist:
                tar_handle.add(file)

    except subprocess.CalledProcessError as e:
        print('... ERROR CODE:\n ... ' + str(e.returncode))
        print('... ERROR MESSAGE:\n ... ' + str(e))

        sys.exit('... could not make installation tar ball!')

    return


def un_tarball(tarball_path):
    '''
    @Description:
        Extracts the given tarball into current directory.

    @Input:
        tarball_path: string
            The complete path to the tar file which will contain all
            relevant data for flex_extract.

    @Return:
        <nothing>
    '''
    import tarfile

    print('Untar ...')

    with tarfile.open(tarball_path) as tar_handle:
        tar_handle.extractall()

    return

def mk_env_vars(ecuid, ecgid, gateway, destination):
    '''
    @Description:
        Creates a file named ECMWF_ENV which contains the
        necessary environmental variables at ECMWF servers.

    @Input:
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

    with open(_config.PATH_RELATIVE_ECMWF_ENV, 'w') as fo:
        fo.write('ECUID ' + ecuid + '\n')
        fo.write('ECGID ' + ecgid + '\n')
        fo.write('GATEWAY ' + gateway + '\n')
        fo.write('DESTINATION ' + destination + '\n')

    return

def mk_compilejob(makefile, target, ecuid, ecgid, fp_root):
    '''
    @Description:
        Modifies the original job template file so that it is specified
        for the user and the environment were it will be applied. Result
        is stored in a new file "job.temp" in the python directory.

    @Input:
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

    template = os.path.join(_config.PATH_RELATIVE_TEMPLATES,
                            _config.TEMPFILE_INSTALL_COMPILEJOB)
    with open(template) as f:
        fdata = f.read().split('\n')

    compilejob = os.path.join(_config.PATH_RELATIVE_JOBSCRIPTS,
                              _config.FILE_INSTALL_COMPILEJOB)
    with open(compilejob, 'w') as fo:
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

def mk_job_template(ecuid, ecgid, gateway, destination, fp_root):
    '''
    @Description:
        Modifies the original job template file so that it is specified
        for the user and the environment were it will be applied. Result
        is stored in a new file.

    @Input:
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
    fp_root_path_to_python = os.path.join(fp_root, _config.FLEXEXTRACT_DIRNAME,
                         _config.PATH_RELATIVE_PYTHON)

    template = os.path.join(_config.PATH_RELATIVE_TEMPLATES,
                            _config.TEMPFILE_INSTALL_JOB)
    with open(template) as f:
        fdata = f.read().split('\n')

    jobfile_temp = os.path.join(_config.PATH_RELATIVE_TEMPLATES,
                                _config.TEMPFILE_JOB)
    with open(jobfile_temp, 'w') as fo:
        for data in fdata:
            if '--workdir' in data:
                data = '#SBATCH --workdir=/scratch/ms/' + ecgid + '/' + ecuid
            elif '##PBS -o' in data:
                data = '##PBS -o /scratch/ms/' + ecgid + '/' + \
                        ecuid + 'flex_ecmwf.$Jobname.$Job_ID.out'
            elif  'export PATH=${PATH}:' in data:
                data += fp_root_path_to_python

            fo.write(data + '\n')
    return

def delete_convert_build(src_path):
    '''
    @Description:
        Clean up the Fortran source directory and remove all
        build files (e.g. *.o, *.mod and CONVERT2)

    @Input:
        src_path: string
            Path to the fortran source directory.

    @Return:
        <nothing>
    '''

    modfiles = UioFiles(src_path, '*.mod')
    objfiles = UioFiles(src_path, '*.o')
    exefile = UioFiles(src_path, _config.FORTRAN_EXECUTABLE)

    modfiles.delete_files()
    objfiles.delete_files()
    exefile.delete_files()

    return

def make_convert_build(src_path, makefile):
    '''
    @Description:
        Compiles the Fortran code and generates the executable.

    @Input:
        src_path: string
            Path to the fortran source directory.

        makefile: string
            The name of the makefile which should be used.

    @Return:
        <nothing>
    '''

    try:
        print('Using makefile: ' + makefile)
        p = subprocess.Popen(['make', '-f',
                              os.path.join(src_path, makefile)],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             bufsize=1)
        pout, perr = p.communicate()
        print(pout)
        if p.returncode != 0:
            print(perr)
            print('Please edit ' + makefile +
                  ' or try another Makefile in the src directory.')
            print('Most likely GRIB_API_INCLUDE_DIR, GRIB_API_LIB '
                  'and EMOSLIB must be adapted.')
            print('Available Makefiles:')
            print(UioFiles(src_path, 'Makefile*'))
            sys.exit('Compilation failed!')
    except ValueError as e:
        print('ERROR: Makefile call failed:')
        print(e)
    else:
        subprocess.check_call(['ls', '-l',
                               os.path.join(src_path,
                                            _config.FORTRAN_EXECUTABLE)])

    return


if __name__ == "__main__":
    main()
