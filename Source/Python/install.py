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
#        - changed static path names to variables from config file
#        - splitted install function into several smaller pieces
#        - use of tarfile package in python
#
# @License:
#    (C) Copyright 2014-2019.
#    Anne Philipp, Leopold Haimberger
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#
# @Methods:
#    main
#    get_install_cmdline_args
#    install_via_gateway
#    check_install_conditions
#    mk_tarball
#    un_tarball
#    mk_env_vars
#    mk_compilejob
#    mk_job_template
#    del_convert_build
#    mk_convert_build
#
#*******************************************************************************
'''This script installs the flex_extract program.

Depending on the selected installation environment (locally or on the
ECMWF server ecgate or cca) the program extracts the commandline
arguments and the CONTROL file parameter and prepares the corresponding
environment.
The necessary files are collected in a tar-ball and placed
at the target location. There its untared, the environment variables will
be set and the Fortran code will be compiled.
If the ECMWF environment is selected a job script is prepared and submitted
for the remaining configurations after putting the tar-ball to the
target ECMWF server.

Type: install.py --help
to get information about command line parameters.
Read the documentation for usage instructions.
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import sys
import glob
import subprocess
import inspect
import tarfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# software specific classes and modules from flex_extract
import _config
from Classes.ControlFile import ControlFile
from Classes.UioFiles import UioFiles
from Mods.tools import (make_dir, put_file_to_ecserver, submit_job_to_ecserver,
                        silent_remove, execute_subprocess, none_or_str)

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
def main():
    '''Controls the installation process. Calls the installation function
    if target is specified.

    Parameters
    ----------

    Return
    ------
    '''

    args = get_install_cmdline_args()
    c = ControlFile(args.controlfile)
    c.assign_args_to_control(args)
    check_install_conditions(c)

    if c.install_target.lower() != 'local': # ecgate or cca
        install_via_gateway(c)
    else: # local
        install_local(c)

    return

def get_install_cmdline_args():
    '''Decomposes the command line arguments and assigns them to variables.
    Apply default values for non mentioned arguments.

    Parameters
    ----------

    Return
    ------
    args : Namespace
        Contains the commandline arguments from script/program call.
    '''
    parser = ArgumentParser(description='Install flex_extract software '
                                        'locally or on ECMWF machines',
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('--target', dest='install_target',
                        type=none_or_str, default=None,
                        help="Valid targets: local | ecgate | cca , \
                        the latter two are at ECMWF")
    parser.add_argument("--makefile", dest="makefile",
                        type=none_or_str, default=None,
                        help='Name of Makefile to use for compiling the '
                        'Fortran program')
    parser.add_argument("--ecuid", dest="ecuid",
                        type=none_or_str, default=None,
                        help='The user id at ECMWF.')
    parser.add_argument("--ecgid", dest="ecgid",
                        type=none_or_str, default=None,
                        help='The group id at ECMWF.')
    parser.add_argument("--gateway", dest="gateway",
                        type=none_or_str, default=None,
                        help='The name of the local gateway server.')
    parser.add_argument("--destination", dest="destination",
                        type=none_or_str, default=None,
                        help='The ecaccess association, e.g. '
                        'myUser@genericSftp')

    parser.add_argument("--installdir", dest="installdir",
                        type=none_or_str, default=None,
                        help='Root directory where '
                        'flex_extract will be installed to.')

    # arguments for job submission to ECMWF, only needed by submit.py
    parser.add_argument("--job_template", dest='job_template',
                        type=none_or_str, default="job.template",
                        help='The rudimentary template file to create a batch '
                        'job template for submission to ECMWF servers.')

    parser.add_argument("--controlfile", dest="controlfile",
                        type=none_or_str, default='CONTROL_EA5',
                        help="The file with all CONTROL parameters.")

    args = parser.parse_args()

    return args


def install_via_gateway(c):
    '''Prepare data transfer to remote gate and submit a job script which will
    install everything on the remote gate.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    import tarfile

    tarball_name = _config.FLEXEXTRACT_DIRNAME + '.tar'
    tar_file = os.path.join(_config.PATH_FLEXEXTRACT_DIR, tarball_name)

    mk_compilejob(c.makefile, c.install_target, c.ecuid, c.ecgid,
                  c.installdir)

    mk_job_template(c.ecuid, c.ecgid, c.gateway,
                    c.destination, c.installdir)

    mk_env_vars(c.ecuid, c.ecgid, c.gateway, c.destination)

    mk_tarball(tar_file, c.install_target)

    put_file_to_ecserver(_config.PATH_FLEXEXTRACT_DIR, tarball_name,
                         c.install_target, c.ecuid, c.ecgid)

    submit_job_to_ecserver(c.install_target,
                           os.path.join(_config.PATH_REL_JOBSCRIPTS,
                                        _config.FILE_INSTALL_COMPILEJOB))

    silent_remove(tar_file)

    print('Job compilation script has been submitted to ecgate for ' +
          'installation in ' + c.installdir +
           '/' + _config.FLEXEXTRACT_DIRNAME)
    print('You should get an email with subject "flexcompile" within ' +
          'the next few minutes!')

    return

def install_local(c):
    '''Perform the actual installation on a local machine.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    import tarfile

    tar_file = os.path.join(_config.PATH_FLEXEXTRACT_DIR,
                            _config.FLEXEXTRACT_DIRNAME + '.tar')

    if c.installdir == _config.PATH_FLEXEXTRACT_DIR :
        print('WARNING: installdir has not been specified')
        print('flex_extract will be installed in here by compiling the ' +
              'Fortran source in ' + _config.PATH_FORTRAN_SRC)
        os.chdir(_config.PATH_FORTRAN_SRC)
    else: # creates the target working directory for flex_extract
        c.installdir = os.path.expandvars(os.path.expanduser(
            c.installdir))
        if os.path.abspath(_config.PATH_FLEXEXTRACT_DIR) != \
           os.path.abspath(c.installdir):
            mk_tarball(tar_file, c.install_target)
            make_dir(os.path.join(c.installdir,
                                   _config.FLEXEXTRACT_DIRNAME))
            os.chdir(os.path.join(c.installdir,
                                   _config.FLEXEXTRACT_DIRNAME))
            un_tarball(tar_file)
            os.chdir(os.path.join(c.installdir,
                                   _config.FLEXEXTRACT_DIRNAME,
                                  _config.PATH_REL_FORTRAN_SRC))

    # Create Fortran executable - CONVERT2
    print('Install ' +  _config.FLEXEXTRACT_DIRNAME + ' software at ' +
          c.install_target + ' in directory ' +
          os.path.abspath(c.installdir) + '\n')

    del_convert_build('.')
    mk_convert_build('.', c.makefile)

    os.chdir(_config.PATH_FLEXEXTRACT_DIR)
    if os.path.isfile(tar_file):
        os.remove(tar_file)

    return


def check_install_conditions(c):
    '''Checks a couple of necessary attributes and conditions
    for the installation such as if they exist and contain values.
    Otherwise set default values.

    Parameters
    ----------
    c : ControlFile
        Contains all the parameters of CONTROL file and
        command line.


    Return
    ------

    '''

    if c.install_target and \
       c.install_target not in _config.INSTALL_TARGETS:
        print('ERROR: unknown or missing installation target ')
        print('target: ', c.install_target)
        print('please specify correct installation target ' +
              str(INSTALL_TARGETS))
        print('use -h or --help for help')
        sys.exit(1)

    if c.install_target and c.install_target != 'local':
        if not c.ecgid or not c.ecuid or \
           not c.gateway or not c.destination:
            print('Please enter your ECMWF user id and group id as well ' +
                  'as the \nname of the local gateway and the ectrans ' +
                  'destination ')
            print('with command line options --ecuid --ecgid \
                   --gateway --destination')
            print('Try "' + sys.argv[0].split('/')[-1] + \
                  ' -h" to print usage information')
            print('Please consult ecaccess documentation or ECMWF user \
                   support for further details')
            sys.exit(1)

        if not c.installdir:
            c.installdir = '${HOME}'
    else: # local
        if not c.installdir:
            c.installdir = _config.PATH_FLEXEXTRACT_DIR

    return


def mk_tarball(tarball_path, target):
    '''Creates a tarball with all necessary files which need to be sent to the
    installation directory.
    It does not matter if this is local or remote.
    Collects all python files, the Fortran source and makefiles,
    the ECMWF_ENV file, the CONTROL files as well as the
    template files.

    Parameters
    ----------
    tarball_path : str
        The complete path to the tar file which will contain all
        relevant data for flex_extract.

    target : str
        The queue where the job is submitted to.

    Return
    ------

    '''
    from glob import glob

    print('Create tarball ...')

    # change to FLEXEXTRACT directory so that the tar can contain
    # relative pathes to the files and directories
    ecd = _config.PATH_FLEXEXTRACT_DIR + '/'
    os.chdir(ecd)

    # get lists of the files to be added to the tar file
    if target == 'local':
        ECMWF_ENV_FILE = []
        runfile = [os.path.relpath(x, ecd)
                   for x in UioFiles(_config.PATH_REL_RUN_DIR,
                                     'run_local.sh').files]
    else:
        ECMWF_ENV_FILE = [_config.PATH_REL_ECMWF_ENV]
        runfile = [os.path.relpath(x, ecd)
                       for x in UioFiles(_config.PATH_REL_RUN_DIR,
                                         'run.sh').files]

    pyfiles = [os.path.relpath(x, ecd)
               for x in UioFiles(_config.PATH_REL_PYTHON_SRC, '*py').files]
    pytestfiles = [os.path.relpath(x, ecd)
               for x in UioFiles(_config.PATH_REL_PYTHONTEST_SRC, '*py').files]
    controlfiles = [os.path.relpath(x, ecd)
                    for x in UioFiles(_config.PATH_REL_CONTROLFILES,
                                      'CONTROL*').files]
    testfiles = [os.path.relpath(x, ecd)
                 for x in UioFiles(_config.PATH_REL_TEST , '*').files]
    tempfiles = [os.path.relpath(x, ecd)
                 for x in UioFiles(_config.PATH_REL_TEMPLATES , '*.temp').files]
    nlfiles = [os.path.relpath(x, ecd)
                 for x in UioFiles(_config.PATH_REL_TEMPLATES , '*.nl').files]
    gribtable = [os.path.relpath(x, ecd)
                 for x in UioFiles(_config.PATH_REL_TEMPLATES , '*grib*').files]
    ffiles = [os.path.relpath(x, ecd)
              for x in UioFiles(_config.PATH_REL_FORTRAN_SRC, '*.f*').files]
    hfiles = [os.path.relpath(x, ecd)
              for x in UioFiles(_config.PATH_REL_FORTRAN_SRC, '*.h').files]
    makefiles = [os.path.relpath(x, ecd)
                 for x in UioFiles(_config.PATH_REL_FORTRAN_SRC, 'Makefile*').files]
    jobdir = [_config.PATH_REL_JOBSCRIPTS]

    # concatenate single lists to one for a better looping
    filelist = pyfiles + pytestfiles + controlfiles + tempfiles + nlfiles + \
               ffiles + gribtable + hfiles + makefiles + ECMWF_ENV_FILE + \
               runfile + jobdir + testfiles +\
               ['CODE_OF_CONDUCT.md', 'LICENSE.md', 'README.md']

    # create installation tar-file
    exclude_files = [".ksh"]
    try:
        with tarfile.open(tarball_path, "w:gz") as tar_handle:
            for file in filelist:
                tar_handle.add(file, recursive=False,
                               filter=lambda tarinfo: None
                                      if os.path.splitext(tarinfo.name)[1]
                                         in exclude_files
                                      else tarinfo)
    except tarfile.TarError as e:
        sys.exit('\n... error occured while trying to create the tar-file ' +
                     str(tarball_path))

    return


def un_tarball(tarball_path):
    '''Extracts the given tarball into current directory.

    Parameters
    ----------
    tarball_path : str
        The complete path to the tar file which will contain all
        relevant data for flex_extract.

    Return
    ------

    '''

    print('Untar ...')

    try:
        with tarfile.open(tarball_path) as tar_handle:
            tar_handle.extractall()
    except tarfile.TarError as e:
        sys.exit('\n... error occured while trying to read tar-file ' +
                     str(tarball_path))
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to read tar-file ' +
                 str(tarball_path))

    return

def mk_env_vars(ecuid, ecgid, gateway, destination):
    '''Creates a file named ECMWF_ENV which contains the
    necessary environmental variables at ECMWF servers.
    It is based on the template ECMWF_ENV.template.

    Parameters
    ----------
    ecuid : str
        The user id on ECMWF server.

    ecgid : str
        The group id on ECMWF server.

    gateway : str
        The gateway server the user is using.

    destination : str
        The remote destination which is used to transfer files
        from ECMWF server to local gateway server.

    Return
    ------

    '''
    from genshi.template.text import NewTextTemplate
    from genshi.template import  TemplateLoader
    from genshi.template.eval import UndefinedError

    try:
        loader = TemplateLoader(_config.PATH_TEMPLATES, auto_reload=False)
        ecmwfvars_template = loader.load(_config.TEMPFILE_USER_ENVVARS,
                                         cls=NewTextTemplate)

        stream = ecmwfvars_template.generate(user_name = ecuid,
                                             user_group = ecgid,
                                             gateway_name = gateway,
                                             destination_name = destination
                                             )
    except UndefinedError as e:
        print('... ERROR ' + str(e))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.PATH_ECMWF_ENV)
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.PATH_ECMWF_ENV)

    try:
        with open(_config.PATH_ECMWF_ENV, 'w') as f:
            f.write(stream.render('text'))
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to write ' +
                 _config.PATH_ECMWF_ENV)

    return

def mk_compilejob(makefile, target, ecuid, ecgid, fp_root):
    '''Modifies the original job template file so that it is specified
    for the user and the environment were it will be applied. Result
    is stored in a new file "job.temp" in the python directory.

    Parameters
    ----------
    makefile : str
        Name of the makefile which should be used to compile FORTRAN
        CONVERT2 program.

    target : str
        The target where the installation should be done, e.g. the queue.

    ecuid : str
        The user id on ECMWF server.

    ecgid : str
        The group id on ECMWF server.

    fp_root : str
       Path to the root directory of FLEXPART environment or flex_extract
       environment.

    Return
    ------

    '''
    from genshi.template.text import NewTextTemplate
    from genshi.template import  TemplateLoader
    from genshi.template.eval import  UndefinedError

    if fp_root == '../':
        fp_root = '$HOME'

    try:
        loader = TemplateLoader(_config.PATH_TEMPLATES, auto_reload=False)
        compile_template = loader.load(_config.TEMPFILE_INSTALL_COMPILEJOB,
                                       cls=NewTextTemplate)

        stream = compile_template.generate(
            usergroup = ecgid,
            username = ecuid,
            version_number = _config._VERSION_STR,
            fp_root_scripts = fp_root,
            makefile = makefile,
            fortran_program = _config.FORTRAN_EXECUTABLE
        )
    except UndefinedError as e:
        print('... ERROR ' + str(e))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.TEMPFILE_INSTALL_COMPILEJOB)
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.TEMPFILE_INSTALL_COMPILEJOB)

    try:
        compilejob = os.path.join(_config.PATH_JOBSCRIPTS,
                                  _config.FILE_INSTALL_COMPILEJOB)

        with open(compilejob, 'w') as f:
            f.write(stream.render('text'))
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to write ' +
                 compilejob)

    return

def mk_job_template(ecuid, ecgid, gateway, destination, fp_root):
    '''Modifies the original job template file so that it is specified
    for the user and the environment were it will be applied. Result
    is stored in a new file.

    Parameters
    ----------
    ecuid : str
        The user id on ECMWF server.

    ecgid : str
        The group id on ECMWF server.

    gateway : str
        The gateway server the user is using.

    destination : str
        The remote destination which is used to transfer files
        from ECMWF server to local gateway server.

    fp_root : str
       Path to the root directory of FLEXPART environment or flex_extract
       environment.

    Return
    ------

    '''
    from genshi.template.text import NewTextTemplate
    from genshi.template import  TemplateLoader
    from genshi.template.eval import  UndefinedError

    fp_root_path_to_python = os.path.join(fp_root,
                                          _config.FLEXEXTRACT_DIRNAME,
                                          _config.PATH_REL_PYTHON_SRC)
    if '$' in fp_root_path_to_python:
        ind = fp_root_path_to_python.index('$')
        fp_root_path_to_python = fp_root_path_to_python[0:ind] + '$' + \
                                 fp_root_path_to_python[ind:]

    try:
        loader = TemplateLoader(_config.PATH_TEMPLATES, auto_reload=False)
        compile_template = loader.load(_config.TEMPFILE_INSTALL_JOB,
                                       cls=NewTextTemplate)

        stream = compile_template.generate(
            usergroup = ecgid,
            username = ecuid,
            version_number = _config._VERSION_STR,
            fp_root_path = fp_root_path_to_python,
        )
    except UndefinedError as e:
        print('... ERROR ' + str(e))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.TEMPFILE_INSTALL_JOB)
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to generate template ' +
                 _config.TEMPFILE_INSTALL_JOB)


    try:
        tempjobfile = os.path.join(_config.PATH_TEMPLATES,
                                   _config.TEMPFILE_JOB)

        with open(tempjobfile, 'w') as f:
            f.write(stream.render('text'))
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to write ' +
                 tempjobfile)

    return

def del_convert_build(src_path):
    '''Clean up the Fortran source directory and remove all
    build files (e.g. \*.o, \*.mod and CONVERT2)

    Parameters
    ----------
    src_path : str
        Path to the fortran source directory.

    Return
    ------

    '''

    modfiles = UioFiles(src_path, '*.mod')
    objfiles = UioFiles(src_path, '*.o')
    exefile = UioFiles(src_path, _config.FORTRAN_EXECUTABLE)

    modfiles.delete_files()
    objfiles.delete_files()
    exefile.delete_files()

    return

def mk_convert_build(src_path, makefile):
    '''Compiles the Fortran code and generates the executable.

    Parameters
    ----------
    src_path : str
        Path to the fortran source directory.

    makefile : str
        The name of the makefile which should be used.

    Return
    ------

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
        print(pout.decode())
        if p.returncode != 0:
            print(perr.decode())
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
        execute_subprocess(['ls', '-l', os.path.join(src_path,
                            _config.FORTRAN_EXECUTABLE)], error_msg=
                           'FORTRAN EXECUTABLE COULD NOT BE FOUND!')

    return


if __name__ == "__main__":
    main()