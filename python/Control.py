#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
# - write a test class
# - check documentation
#************************************************************************
"""
@Author: Leopold Haimberger (University of Vienna)

@Date: November 2015

@ChangeHistory:
   February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - applied some minor modifications in programming style/structure
        - outsource of class Control

@License:
    (C) Copyright 2015-2018.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    A standard python 2.6 or 2.7 installation

@Description:
    The Control files are the steering part of the FLEXPART extraction
    software. All necessary parameters needed to retrieve the data fields
    from the MARS archive for driving FLEXPART are set in a Control file.
    Some specific parameters like the start and end dates can be overwritten
    by the command line parameters, but in generel all parameters needed
    for a complete set of fields for FLEXPART can be set in the Control files.

"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import os
import inspect
import Tools
# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class Control:
    '''
    Class containing the information of the ECMWFDATA control file.

    Contains all the parameters of control files, which are e.g.:
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
            Initialises the instance of Control class and defines and
            assign all controlfile variables. Set default values if
            parameter was not in CONTROL file.

        @Input:
            self: instance of Control class
                Description see class documentation.

            filename: string
                Name of control file.

        @Return:
            <nothing>
        '''

        # read whole CONTROL file
        with open(filename) as f:
            fdata = f.read().split('\n')

        # go through every line and store parameter
        # as class variable
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
                    pass
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
                                Tools.myerror(None,
                                              'Could not find variable ' +
                                              data[1][j+1:k] +
                                              ' while reading ' +
                                              filename)
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

        # check a couple of necessary attributes if they contain values
        # otherwise set default values
        if not hasattr(self, 'start_date'):
            self.start_date = None
        if not hasattr(self, 'end_date'):
            self.end_date = self.start_date
        if not hasattr(self, 'accuracy'):
            self.accuracy = 24
        if not hasattr(self, 'omega'):
            self.omega = '0'
        if not hasattr(self, 'cwc'):
            self.cwc = '0'
        if not hasattr(self, 'omegadiff'):
            self.omegadiff = '0'
        if not hasattr(self, 'etadiff'):
            self.etadiff = '0'
        if not hasattr(self, 'levelist'):
            if not hasattr(self, 'level'):
                print('Warning: neither levelist nor level \
                       specified in CONTROL file')
            else:
                self.levelist = '1/to/' + self.level
        else:
            if 'to' in self.levelist:
                self.level = self.levelist.split('/')[2]
            else:
                self.level = self.levelist.split('/')[-1]

        if not hasattr(self, 'maxstep'):
            # find out maximum step
            self.maxstep = 0
            for s in self.step:
                if int(s) > self.maxstep:
                    self.maxstep = int(s)
        else:
            self.maxstep = int(self.maxstep)

        if not hasattr(self, 'prefix'):
            self.prefix = 'EN'
        if not hasattr(self, 'makefile'):
            self.makefile = None
        if not hasattr(self, 'basetime'):
            self.basetime = None
        if not hasattr(self, 'date_chunk'):
            self.date_chunk = '3'
        if not hasattr(self, 'grib2flexpart'):
            self.grib2flexpart = '0'

        # script directory
        self.ecmwfdatadir = os.path.dirname(os.path.abspath(inspect.getfile(
            inspect.currentframe()))) + '/../'
        # Fortran source directory
        self.exedir = self.ecmwfdatadir + 'src/'

        # FLEXPART directory
        if not hasattr(self, 'flexpart_root_scripts'):
            self.flexpart_root_scripts = self.ecmwfdatadir

        return

    def __str__(self):
        '''
        @Description:
            Prepares a single string with all the comma seperated Control
            class attributes including their values.

            Example:
            {'kids': 0, 'name': 'Dog', 'color': 'Spotted',
             'age': 10, 'legs': 2, 'smell': 'Alot'}

        @Input:
            self: instance of Control class
                Description see class documentation.

        @Return:
            string of Control class attributes with their values
        '''

        attrs = vars(self)

        return ', '.join("%s: %s" % item for item in attrs.items())

    def tolist(self):
        '''
        @Description:
            Just generates a list of strings containing the attributes and
            assigned values except the attributes "_expanded", "exedir",
            "ecmwfdatadir" and "flexpart_root_scripts".

        @Input:
            self: instance of Control class
                Description see class documentation.

        @Return:
            l: list
                A sorted list of the all Control class attributes with
                their values except the attributes "_expanded", "exedir",
                "ecmwfdatadir" and "flexpart_root_scripts".
        '''

        attrs = vars(self)
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
                if type(item[1]) is list:
                    stot = ''
                    for s in item[1]:
                        stot += s + ' '

                    l.append("%s %s" % (item[0], stot))
                else:
                    l.append("%s %s" % item)

        return sorted(l)
