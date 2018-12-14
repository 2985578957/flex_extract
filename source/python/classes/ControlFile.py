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
import numpy as np

# software specific classes and modules from flex_extract
sys.path.append('../')
import _config
from mods.tools import my_error, silent_remove
from mods.checks import (check_grid, check_area, check_levels, check_purefc,
                         check_step, check_mail, check_queue, check_pathes,
                         check_dates, check_maxstep, check_type, check_request,
                         check_basetime, check_public, check_acctype,
                         check_acctime, check_accmaxstep, check_time,
                         check_logicals_type, check_len_type_time_step,
                         check_addpar, check_job_chunk)

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class ControlFile(object):
    '''
    Contains the information which are stored in the CONTROL files.
    '''

    def __init__(self, filename):
        '''Initialises the instance of ControlFile class and defines
        all class attributes with default values. Afterwards calls
        function __read_controlfile__ to read parameter from Control file.

        Parameters
        ----------
        filename : :obj:`string`
            Name of CONTROL file.

        Return
        ------

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
        self.acctype = None
        self.acctime = None
        self.accmaxstep = None
        self.marsclass = None
        self.dataset = None
        self.stream = None
        self.number = 'OFF'
        self.expver = '1'
        self.gaussian = ''
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
        self.flexextractdir = _config.PATH_FLEXEXTRACT_DIR
        self.exedir = _config.PATH_FORTRAN_SRC
        self.flexpartdir = None
        self.makefile = 'Makefile.gfortran'
        self.destination = None
        self.gateway = None
        self.ecuid = None
        self.ecgid = None
        self.install_target = None
        self.debug = 0
        self.request = 0
        self.public = 0
        self.ecapi = None
        self.purefc = 0
        self.rrint = 0

        self.logicals = ['gauss', 'omega', 'omegadiff', 'eta', 'etadiff',
                         'dpdeta', 'cwc', 'wrf', 'grib2flexpart', 'ecstorage',
                         'ectrans', 'debug', 'request', 'public', 'purefc',
                         'rrint']

        self._read_controlfile()

        return

    def _read_controlfile(self):
        '''Read CONTROL file and assign all CONTROL file variables.

        Parameters
        ----------

        Return
        ------

        '''

        try:
            cfile = os.path.join(_config.PATH_CONTROLFILES, self.controlfile)
            with open(cfile) as f:
                fdata = f.read().split('\n')
        except IOError:
            print('Could not read CONTROL file "' + cfile + '"')
            print('Either it does not exist or its syntax is wrong.')
            print('Try "' + sys.argv[0].split('/')[-1] + \
                      ' -h" to print usage information')
            sys.exit(1)

        # go through every line and store parameter
        for ldata in fdata:
            if ldata and ldata[0] == '#':
                # ignore comment line in control file
                continue
            if '#' in ldata:
                # cut off comment
                ldata = ldata.split('#')[0]
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
        '''Prepares a string which have all the ControlFile class attributes
        with its associated values. Each attribute is printed in one line and
        in alphabetical order.

        Example
        -------
        'age': 10
        'color': 'Spotted'
        'kids': 0
        'legs': 2
        'name': 'Dog'
        'smell': 'Alot'

        Parameters
        ----------

        Return
        ------
        string
            Single string of concatenated ControlFile class attributes
            with their values
        '''
        import collections

        attrs = vars(self).copy()
        attrs = collections.OrderedDict(sorted(attrs.items()))

        return '\n'.join("%s: %s" % item for item in attrs.items())

    def assign_args_to_control(self, args):
        '''Overwrites the existing ControlFile instance attributes with
        the command line arguments.

        Parameters
        ----------
        args : :obj:`Namespace`
            Contains the commandline arguments from script/program call.

        Return
        ------

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
        '''Assigns the ECMWF environment parameter.

        Parameters
        ----------
        envs : :obj:`dictionary` of :obj:`strings`
            Contains the ECMWF environment parameternames "ECUID", "ECGID",
            "DESTINATION" and "GATEWAY" with its corresponding values.
            They were read from the file "ECMWF_ENV".

        Return
        ------

        '''

        for k, v in envs.iteritems():
            setattr(self, str(k).lower(), str(v))

        return

    def check_conditions(self, queue):
        '''Checks a couple of necessary attributes and conditions,
        such as if they exist and contain values.
        Otherwise set default values.

        Parameters
        ----------
        queue : :obj:`string`
            Name of the queue if submitted to the ECMWF servers.
            Used to check if ecuid, ecgid, gateway and destination
            are set correctly and are not empty.

        Return
        ------

        '''
        check_logicals_type(self, self.logicals)

        self.mailfail = check_mail(self.mailfail)

        self.mailops = check_mail(self.mailops)

        check_queue(queue, self.gateway, self.destination,
                    self.ecuid, self.ecgid)

        self.outputdir, self.flexpartdir = check_pathes(self.inputdir,
             self.outputdir, self.flexpartdir, self.flexextractdir)

        self.start_date, self.end_date = check_dates(self.start_date,
                                                     self.end_date)

        check_basetime(self.basetime)

        self.levelist, self.level = check_levels(self.levelist, self.level)

        self.step = check_step(self.step, self.mailfail)

        self.maxstep = check_maxstep(self.maxstep, self.step)

        check_request(self.request,
                      os.path.join(self.inputdir, _config.FILE_MARS_REQUESTS))

        check_public(self.public, self.dataset)

        self.type = check_type(self.type, self.step)

        self.time = check_time(self.time)

        self.type, self.time, self.step = check_len_type_time_step(self.type,
                                                                   self.time,
                                                                   self.step,
                                                                   self.maxstep,
                                                                   self.purefc)

        self.acctype = check_acctype(self.acctype, self.type)

        self.acctime = check_acctime(self.acctime, self.acctype, self.purefc)

        self.accmaxstep = check_accmaxstep(self.accmaxstep, self.acctype,
                                           self.purefc, self.maxstep)

        self.purefc = check_purefc(self.type)

        self.grid = check_grid(self.grid)

        self.area = check_area(self.grid, self.area, self.upper, self.lower,
                               self.left, self.right)

        self.addpar = check_addpar(self.addpar)

        self.job_chunk = check_job_chunk(self.job_chunk)

        return

    def to_list(self):
        '''Just generates a list of strings containing the attributes and
        assigned values except the attributes "_expanded", "exedir",
        "flexextractdir" and "flexpartdir".

        Parameters
        ----------

        Return
        ------
        l : :obj:`list`
            A sorted list of the all ControlFile class attributes with
            their values except the attributes "_expanded", "exedir",
            "flexextractdir" and "flexpartdir".
        '''

        import collections

        attrs = collections.OrderedDict(sorted(vars(self).copy().items()))

        l = list()

        for item in attrs.items():
            if '_expanded' in item[0]:
                pass
            elif 'exedir' in item[0]:
                pass
            elif 'flexpartdir' in item[0]:
                pass
            elif 'flexextractdir' in item[0]:
                pass
            else:
                if isinstance(item[1], list):
                    stot = ''
                    for s in item[1]:
                        stot += s + ' '

                    l.append("%s %s\n" % (item[0], stot))
                else:
                    l.append("%s %s\n" % item)

        return sorted(l)

