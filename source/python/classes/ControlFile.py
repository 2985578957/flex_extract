#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Leopold Haimberger (University of Vienna)
#
# @Date: November 2015
#
# @Change History:
#
#   February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - applied some minor modifications in programming style/structure
#        - changed name of class Control to ControlFile for more
#          self-explanation naming
#        - outsource of class ControlFile
#        - initialisation of class attributes ( to avoid high number of
#          conditional statements and set default values )
#        - divided assignment of attributes and the check of conditions
#        - outsourced the commandline argument assignments to control attributes
#
# @License:
#    (C) Copyright 2015-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Class Description:
#    The CONTROL file is the steering part of the FLEXPART extraction
#    software. All necessary parameters needed to retrieve the data fields
#    from the MARS archive for driving FLEXPART are set in a CONTROL file.
#    Some specific parameters like the start and end dates can be overwritten
#    by the command line parameters, but in generel all parameters needed
#    for a complete set of fields for FLEXPART can be set in the CONTROL file.
#
# @Class Content:
#    - __init__
#    - __read_controlfile__
#    - __str__
#    - assign_args_to_control
#    - assign_envs_to_control
#    - check_conditions
#    - check_install_conditions
#    - to_list
#
# @Class Attributes:
#
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import re
import sys
import inspect

# software specific classes and modules from flex_extract
sys.path.append('../')
import _config
from mods.tools import my_error

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class ControlFile(object):
    '''
    Class containing the information of the flex_extract CONTROL file.

    Contains all the parameters of CONTROL file, which are e.g.:
    DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
    STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
    LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
    OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
    ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
    MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR,
    BASETIME, DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

    For more information about format and content of the parameter
    see documentation.

    '''

    def __init__(self, filename):
        '''
        @Description:
            Initialises the instance of ControlFile class and defines
            all class attributes with default values. Afterwards calls
            function __read_controlfile__ to read parameter from
            Control file.

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

            filename: string
                Name of CONTROL file.

        @Return:
            <nothing>
        '''

        # list of all possible class attributes and their default values
        self.controlfile = filename
        self.start_date = None
        self.end_date = None
        self.date_chunk = 3
        self.dtime = None
        self.basetime = None
        self.maxstep = None
        self.type = None
        self.time = None
        self.step = None
        self.marsclass = None
        self.dataset = None
        self.stream = None
        self.number = 'OFF'
        self.expver = '1'
        self.grid = None
        self.area = ''
        self.left = None
        self.lower = None
        self.upper = None
        self.right = None
        self.level = None
        self.levelist = None
        self.resol = None
        self.gauss = 0
        self.accuracy = 24
        self.omega = 0
        self.omegadiff = 0
        self.eta = 0
        self.etadiff = 0
        self.etapar = 77
        self.dpdeta = 1
        self.smooth = 0
        self.format = 'GRIB1'
        self.addpar = None
        self.prefix = 'EN'
        self.cwc = 0
        self.wrf = 0
        self.ecfsdir = 'ectmp:/${USER}/econdemand/'
        self.mailfail = ['${USER}']
        self.mailops = ['${USER}']
        self.grib2flexpart = 0
        self.ecstorage = 0
        self.ectrans = 0
        self.inputdir = _config.PATH_INPUT_DIR
        self.outputdir = None
        self.ecmwfdatadir = _config.PATH_FLEXEXTRACT_DIR
        self.exedir = _config.PATH_FORTRAN_SRC
        self.flexpart_root_scripts = None
        self.makefile = 'Makefile.gfortran'
        self.destination = None
        self.gateway = None
        self.ecuid = None
        self.ecgid = None
        self.install_target = None
        self.debug = 0
        self.request = 0
        self.public = 0

        self.logicals = ['gauss', 'omega', 'omegadiff', 'eta', 'etadiff',
                         'dpdeta', 'cwc', 'wrf', 'grib2flexpart', 'ecstorage',
                         'ectrans', 'debug', 'request', 'public']

        self.__read_controlfile__()

        return

    def __read_controlfile__(self):
        '''
        @Description:
            Read CONTROL file and assign all CONTROL file variables.

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

        @Return:
            <nothing>
        '''

        try:
            with open(os.path.join(_config.PATH_CONTROLFILES,
                                   self.controlfile)) as f:
                fdata = f.read().split('\n')
        except IOError:
            print('Could not read CONTROL file "' + args.controlfile + '"')
            print('Either it does not exist or its syntax is wrong.')
            print('Try "' + sys.argv[0].split('/')[-1] + \
                      ' -h" to print usage information')
            sys.exit(1)

        # go through every line and store parameter
        for ldata in fdata:
            data = ldata.split()
            if len(data) > 1:
                if 'm_' in data[0].lower():
                    data[0] = data[0][2:]
                if data[0].lower() == 'class':
                    data[0] = 'marsclass'
                if data[0].lower() == 'day1':
                    data[0] = 'start_date'
                if data[0].lower() == 'day2':
                    data[0] = 'end_date'
                if data[0].lower() == 'addpar':
                    if '/' in data[1]:
                        # remove leading '/' sign from addpar content
                        if data[1][0] == '/':
                            data[1] = data[1][1:]
                        dd = data[1].split('/')
                        data = [data[0]]
                        for d in dd:
                            data.append(d)
                if len(data) == 2:
                    if '$' in data[1]:
                        setattr(self, data[0].lower(), data[1])
                        while '$' in data[1]:
                            i = data[1].index('$')
                            j = data[1].find('{')
                            k = data[1].find('}')
                            var = os.getenv(data[1][j+1:k])
                            if var is not None:
                                data[1] = data[1][:i] + var + data[1][k+1:]
                            else:
                                my_error(self.mailfail,
                                         'Could not find variable '
                                         + data[1][j+1:k] + ' while reading ' +
                                         self.controlfile)
                        setattr(self, data[0].lower() + '_expanded', data[1])
                    else:
                        if data[1].lower() != 'none':
                            setattr(self, data[0].lower(), data[1])
                        else:
                            setattr(self, data[0].lower(), None)
                elif len(data) > 2:
                    setattr(self, data[0].lower(), (data[1:]))
            else:
                pass

        return

    def __str__(self):
        '''
        @Description:
            Prepares a string which have all the ControlFile
            class attributes with its associated values.
            Each attribute is printed in one line and in
            alphabetical order.

            Example:
            'age': 10
            'color': 'Spotted'
            'kids': 0
            'legs': 2
            'name': 'Dog'
            'smell': 'Alot'

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

        @Return:
            string of ControlFile class attributes with their values
        '''
        import collections

        attrs = vars(self).copy()
        attrs = collections.OrderedDict(sorted(attrs.items()))

        return '\n'.join("%s: %s" % item for item in attrs.items())

    def assign_args_to_control(self, args):
        '''
        @Description:
            Overwrites the existing ControlFile instance attributes with
            the command line arguments.

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

            args: instance of ArgumentParser
                Contains the commandline arguments from script/program call.

        @Return:
            <nothing>
        '''

        # get dictionary of command line parameters and eliminate all
        # parameters which are None (were not specified)
        args_dict = vars(args)
        arguments = {k : args_dict[k] for k in args_dict
                     if args_dict[k] != None}

        # assign all passed command line arguments to ControlFile instance
        for k, v in arguments.iteritems():
            setattr(self, str(k), v)

        return

    def assign_envs_to_control(self, envs):
        '''
        @Description:
            Assigns the ECMWF environment parameter.

        @Input:
            envs: dict of strings
                Contains the ECMWF environment parameternames "ECUID", "ECGID",
                "DESTINATION" and "GATEWAY" with its corresponding values.
                They were read from the file "ECMWF_ENV".

        @Return:
            <nothing>
        '''

        for k, v in envs.iteritems():
            setattr(self, str(k).lower(), str(v))

        return

    def check_conditions(self, queue):
        '''
        @Description:
            Checks a couple of necessary attributes and conditions,
            such as if they exist and contain values.
            Otherwise set default values.

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

            queue: string
                Name of the queue if submitted to the ECMWF servers.
                Used to check if ecuid, ecgid, gateway and destination
                are set correctly and are not empty.

        @Return:
            <nothing>
        '''
        from mods.tools import my_error
        import numpy as np

        # check for having at least a starting date
        # otherwise program is not allowed to run
        if self.start_date is None:
            print('start_date specified neither in command line nor \
                   in CONTROL file ' +  self.controlfile)
            print('Try "' + sys.argv[0].split('/')[-1] +
                  ' -h" to print usage information')
            sys.exit(1)

        # retrieve just one day if end_date isn't set
        if self.end_date is None:
            self.end_date = self.start_date

        # basetime has only two possible values
        if self.basetime:
            if int(self.basetime) != 0 and int(self.basetime) != 12:
                print('Basetime has an invalid value!')
                print('Basetime = ' + str(self.basetime))
                sys.exit(1)

        # assure consistency of levelist and level
        if self.levelist is None and self.level is None:
            print('Warning: neither levelist nor level \
                               specified in CONTROL file')
            sys.exit(1)
        elif self.levelist is None and self.level:
            self.levelist = '1/to/' + self.level
        elif (self.levelist and self.level is None) or \
             (self.levelist[-1] != self.level[-1]):
            self.level = self.levelist.split('/')[-1]
        else:
            pass

        # if area was provided (only from commandline)
        # decompose area into its 4 components
        if self.area:
            components = self.area.split('/')
            # convert float to integer coordinates
            if '.' in self.area:
                components = [str(int(float(item) * 1000))
                              for i, item in enumerate(components)]
            self.upper, self.left, self.lower, self.right = components

        # prepare step list if "/" signs are found
        if '/' in self.step:
            steps = self.step.split('/')
            if 'to' in self.step.lower() and 'by' in self.step.lower():
                ilist = np.arange(int(steps[0]),
                                  int(steps[2]) + 1,
                                  int(steps[4]))
                self.step = ['{:0>3}'.format(i) for i in ilist]
            elif 'to' in self.step.lower() and 'by' not in self.step.lower():
                my_error(self.mailfail, self.step + ':\n' +
                         'if "to" is used in steps parameter, \
                         please use "by" as well')
            else:
                self.step = steps

        # if maxstep wasn't provided
        # search for it in the "step" parameter
        if self.maxstep is None:
            self.maxstep = 0
            for s in self.step:
                if int(s) > self.maxstep:
                    self.maxstep = int(s)
        else:
            self.maxstep = int(self.maxstep)

        # set root scripts since it is needed later on
        if not self.flexpart_root_scripts:
            self.flexpart_root_scripts = self.ecmwfdatadir

        if not self.outputdir:
            self.outputdir = self.inputdir

        if not isinstance(self.mailfail, list):
            if ',' in self.mailfail:
                self.mailfail = self.mailfail.split(',')
            elif ' ' in self.mailfail:
                self.mailfail = self.mailfail.split()
            else:
                self.mailfail = [self.mailfail]

        if not isinstance(self.mailops, list):
            if ',' in self.mailops:
                self.mailops = self.mailops.split(',')
            elif ' ' in self.mailops:
                self.mailops = self.mailops.split()
            else:
                self.mailops = [self.mailops]

        if queue in ['ecgate', 'cca'] and \
           not self.gateway or not self.destination or \
           not self.ecuid or not self.ecgid:
            print('\nEnvironment variables GATEWAY, DESTINATION, ECUID and \
                   ECGID were not set properly!')
            print('Please check for existence of file "ECMWF_ENV" in the \
                   python directory!')
            sys.exit(1)

        if self.request != 0:
            marsfile = os.path.join(self.inputdir,
                                    _config.FILE_MARS_REQUESTS)
            if os.path.isfile(marsfile):
                os.remove(marsfile)

        # check all logical variables for data type
        # if its a string change to integer
        for var in self.logicals:
            if not isinstance(getattr(self, var), int):
                setattr(self, var, int(getattr(self, var)))

        if self.public and not self.dataset:
            print('ERROR: ')
            print('If public mars data wants to be retrieved, '
                  'the "dataset"-parameter has to be set in the control file!')
            sys.exit(1)

        return

    def check_install_conditions(self):
        '''
        @Description:
            Checks a couple of necessary attributes and conditions
            for the installation such as if they exist and contain values.
            Otherwise set default values.

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

        @Return:
            <nothing>
        '''

        if self.install_target and \
           self.install_target not in ['local', 'ecgate', 'cca']:
            print('ERROR: unknown or missing installation target ')
            print('target: ', self.install_target)
            print('please specify correct installation target ' +
                  '(local | ecgate | cca)')
            print('use -h or --help for help')
            sys.exit(1)

        if self.install_target and self.install_target != 'local':
            if not self.ecgid or not self.ecuid or \
               not self.gateway or not self.destination:
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

            if not self.flexpart_root_scripts:
                self.flexpart_root_scripts = '${HOME}'
            else:
                self.flexpart_root_scripts = self.flexpart_root_scripts
        else: # local
            if not self.flexpart_root_scripts:
                self.flexpart_root_scripts = _config.PATH_FLEXEXTRACT_DIR

        return

    def to_list(self):
        '''
        @Description:
            Just generates a list of strings containing the attributes and
            assigned values except the attributes "_expanded", "exedir",
            "ecmwfdatadir" and "flexpart_root_scripts".

        @Input:
            self: instance of ControlFile class
                Description see class documentation.

        @Return:
            l: list
                A sorted list of the all ControlFile class attributes with
                their values except the attributes "_expanded", "exedir",
                "ecmwfdatadir" and "flexpart_root_scripts".
        '''

        import collections

        attrs = collections.OrderedDict(sorted(vars(self).copy().items()))

        l = list()

        for item in attrs.items():
            if '_expanded' in item[0]:
                pass
            elif 'exedir' in item[0]:
                pass
            elif 'flexpart_root_scripts' in item[0]:
                pass
            elif 'ecmwfdatadir' in item[0]:
                pass
            else:
                if isinstance(item[1], list):
                    stot = ''
                    for s in item[1]:
                        stot += s + ' '

                    l.append("%s %s" % (item[0], stot))
                else:
                    l.append("%s %s" % item)

        return sorted(l)

