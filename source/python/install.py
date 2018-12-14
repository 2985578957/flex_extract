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
#    - get_install_cmdline_args
#    - install_via_gateway
#    - mk_tarball
#    - un_tarball
#    - mk_env_vars
#    - mk_compilejob
#    - mk_job_template
#    - del_convert_build
#    - mk_convert_build
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
import tarfile
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# software specific classes and modules from flex_extract
import _config
from classes.ControlFile import ControlFile
from classes.UioFiles import UioFiles
from mods.tools import (make_dir, put_file_to_ecserver, submit_job_to_ecserver,
                        silent_remove)

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

    install_via_gateway(c)

    return

def get_install_cmdline_args():
    '''Decomposes the command line arguments and assigns them to variables.
    Apply default values for non mentioned arguments.

    Parameters
    ----------

    Return
    ------
    args : :obj:`Namespace`
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

    parser.add_argument("--flexpartdir", dest="flexpartdir",
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
    '''Perform the actual installation on local machine or prepare data
    transfer to remote gate and submit a job script which will
    install everything on the remote gate.

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    Return
    ------

    '''
    import tarfile

    ecd = _config.PATH_FLEXEXTRACT_DIR
    tarball_name = _config.FLEXEXTRACT_DIRNAME + '.tar'
    tar_file = os.path.join(ecd, tarball_name)

    target_dirname = _config.FLEXEXTRACT_DIRNAME
    fortran_executable = _config.FORTRAN_EXECUTABLE

    if c.install_target.lower() != 'local': # ecgate or cca

        mk_compilejob(c.makefile, c.install_target, c.ecuid, c.ecgid,
                      c.flexpartdir)

        mk_job_template(c.ecuid, c.ecgid, c.gateway,
                        c.destination, c.flexpartdir)

        mk_env_vars(c.ecuid, c.ecgid, c.gateway, c.destination)

        mk_tarball(tar_file, c.install_target)

        put_file_to_ecserver(ecd, tarball_name, c.install_target,
                             c.ecuid, c.ecgid)

        submit_job_to_ecserver(c.install_target,
                               os.path.join(_config.PATH_REL_JOBSCRIPTS,
                                            _config.FILE_INSTALL_COMPILEJOB))

        silent_remove(tar_file)

        print('job compilation script has been submitted to ecgate for ' +
              'installation in ' + c.flexpartdir +
               '/' + target_dirname)
        print('You should get an email with subject "flexcompile" within ' +
              'the next few minutes!')

    else: #local
        if c.flexpartdir == _config.PATH_FLEXEXTRACT_DIR :
            print('WARNING: FLEXPARTDIR has not been specified')
            print('flex_extract will be installed in here by compiling the ' +
                  'Fortran source in ' + _config.PATH_FORTRAN_SRC)
            os.chdir(_config.PATH_FORTRAN_SRC)
        else: # creates the target working directory for flex_extract
            c.flexpartdir = os.path.expandvars(os.path.expanduser(
                                        c.flexpartdir))
            if os.path.abspath(ecd) != os.path.abspath(c.flexpartdir):
                mk_tarball(tar_file, c.install_target)
                make_dir(os.path.join(c.flexpartdir,
                                      target_dirname))
                os.chdir(os.path.join(c.flexpartdir,
                                      target_dirname))
                un_tarball(tar_file)
                os.chdir(os.path.join(c.flexpartdir,
                                      target_dirname,
                                      _config.PATH_REL_FORTRAN_SRC))

        # Create Fortran executable - CONVERT2
        print('Install ' + target_dirname + ' software at ' +
              c.install_target + ' in directory ' +
              os.path.abspath(c.flexpartdir) + '\n')

        del_convert_build('.')
        mk_convert_build('.', c.makefile)

        os.chdir(ecd)
        if os.path.isfile(tar_file):
            os.remove(tar_file)

    return

def check_install_conditions(c):
    '''Checks a couple of necessary attributes and conditions
    for the installation such as if they exist and contain values.
    Otherwise set default values.

    Parameters
    ----------
    c : :obj:`ControlFile`
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

        if not c.flexpartdir:
            c.flexpartdir = '${HOME}'
        else:
            c.flexpartdir = c.flexpartdir
    else: # local
        if not c.flexpartdir:
            c.flexpartdir = _config.PATH_FLEXEXTRACT_DIR

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
    tarball_path : :obj:`string`
        The complete path to the tar file which will contain all
        relevant data for flex_extract.

    target : :obj:`string`
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
               runfile + jobdir + \
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
    except subprocess.CalledProcessError as e:
        print('... ERROR CODE:\n ... ' + str(e.returncode))
        print('... ERROR MESSAGE:\n ... ' + str(e))

        sys.exit('\n... could not make installation tar ball!')
    except OSError as e:
        print('... ERROR CODE: ' + str(e.errno))
        print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

        sys.exit('\n... error occured while trying to read tar-file ' +
                 str(tarball_path))

    return


def un_tarball(tarball_path):
    '''Extracts the given tarball into current directory.

    Parameters
    ----------
    tarball_path : :obj:`string`
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
    ecuid : :obj:`string`
        The user id on ECMWF server.

    ecgid : :obj:`string`
        The group id on ECMWF server.

    gateway : :obj:`string`
        The gateway server the user is using.

    destination : :obj:`string`
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
    makefile : :obj:`string`
        Name of the makefile which should be used to compile FORTRAN
        CONVERT2 program.

    target : :obj:`string`
        The target where the installation should be done, e.g. the queue.

    ecuid : :obj:`string`
        The user id on ECMWF server.

    ecgid : :obj:`string`
        The group id on ECMWF server.

    fp_root : :obj:`string`
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
    ecuid : :obj:`string`
        The user id on ECMWF server.

    ecgid : :obj:`string`
        The group id on ECMWF server.

    gateway : :obj:`string`
        The gateway server the user is using.

    destination : :obj:`string`
        The remote destination which is used to transfer files
        from ECMWF server to local gateway server.

    fp_root : :obj:`string`
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
    src_path : :obj:`string`
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
    src_path : :obj:`string`
        Path to the fortran source directory.

    makefile : :obj:`string`
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
