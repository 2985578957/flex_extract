#!/usr/bin/env python3
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
#   June 2020 - Anne Philipp
#        - update default makefile to None
#
# @License:
#    (C) Copyright 2014-2020.
#    Anne Philipp, Leopold Haimberger
#
#    SPDX-License-Identifier: CC-BY-4.0
#
#    This work is licensed under the Creative Commons Attribution 4.0
#    International License. To view a copy of this license, visit
#    http://creativecommons.org/licenses/by/4.0/ or send a letter to
#    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import sys

# software specific classes and modules from flex_extract
#pylint: disable=wrong-import-position
sys.path.append('../')
import _config
from Mods.tools import my_error
from Mods.checks import (check_grid, check_area, check_levels, check_purefc,
                         check_step, check_mail, check_queue, check_pathes,
                         check_dates, check_maxstep, check_type, check_request,
                         check_basetime, check_public, check_acctype,
                         check_acctime, check_accmaxstep, check_time,
                         check_logicals_type, check_len_type_time_step,
                         check_addpar, check_job_chunk, check_number)
#pylint: enable=wrong-import-position

# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class ControlFile(object):
    '''
    Contains the information which are stored in the CONTROL files.

    The CONTROL file is the steering part of the FLEXPART extraction
    software. All necessary parameters needed to retrieve the data fields
    from the MARS archive for driving FLEXPART are set in a CONTROL file.
    Some specific parameters like the start and end dates can be overwritten
    by the command line parameters, but in generall all parameters needed
    for a complete set of fields for FLEXPART can be set in the CONTROL file.

    Attributes
    ----------
    controlfile : str
        The name of the control file to be processed. Default value is the
        filename passed to the init function when initialised.

    start_date : str
        The first day of the retrieval period. Default value is None.

    end_date :str
        The last day of the retrieval period. Default value is None.

    date_chunk : int
        Length of period for a single mars retrieval. Default value is 3.

    dtime :str
        The time step in hours. Default value is None.

    basetime : int
        The time for a half day retrieval. The 12 hours upfront are to be
        retrieved. Default value is None.

    maxstep : int
        The maximum forecast step for non flux data. Default value is None.

    type : list of str
        List of field type per retrieving hour. Default value is None.

    time : list of str
        List of retrieving times in hours. Default valuer is None.

    step : list of str or str
        List of forecast time steps in hours for non flux data.
        Default value is None.

    acctype : str
        The field type for the accumulated forecast fields.
        Default value is None.

    acctime : str
        The starting time of the accumulated forecasts. Default value is None.

    accmaxstep : int
        The maximum forecast step for the accumulated forecast fields
        (flux data). Default value is None.

    marsclass : str
        Characterisation of dataset. Default value is None.

    dataset : str
        For public datasets there is the specific naming and parameter
        dataset which has to be used to characterize the type of
        data. Default value is None.

    stream : str
        Identifies the forecasting system used to generate the data.
        Default value is None.

    number : str
        Selects the member in ensemble forecast run. Default value is 'OFF'.

    expver : str
        The version number of the dataset. Default value is '1'.

    gaussian : str
        This parameter is deprecated and should no longer be used.
        Specifies the desired type of Gaussian grid for the output.
        Default value is an empty string ''.

    grid : str
        Specifies the output grid which can be either a Gaussian grid
        or a Latitude/Longitude grid. Default value is None.

    area : str
        Specifies the desired sub-area of data to be extracted.
        Default value is None.

    left : str
        The western most longitude of the area to be extracted.
        Default value is None.

    lower : str
        The southern most latitude of the area to be extracted.
        Default value is None.

    upper : str
        The northern most latitued of the area to be extracted.
        Default value is None.

    right : str
        The eastern most longitude of the area to be extracted.
        Default value is None.

    level : str
        Specifies the maximum level. Default value is None.

    levelist : str
        Specifies the required level list. Default value is None.

    resol : str
        Specifies the desired triangular truncation of retrieved data,
        before carrying out any other selected post-processing.
        Default value is None.

    gauss : int
        Switch to select gaussian fields (1) or regular lat/lon (0).
        Default value is 0.

    accuracy : int
        Specifies the number of bits per value to be used in the
        generated GRIB coded fields. Default value is 24.

    omega : int
       Switch to select omega retrieval (1) or not (0). Default value is 0.

    omegadiff : int
        Switch to decide to calculate Omega and Dps/Dt from continuity
        equation for diagnostic purposes (1) or not (0). Default value is 0.

    eta : int
        Switch to select direct retrieval of etadot from MARS (1) or
        wether it has to be calculated (0). Then Default value is 0.

    etadiff : int
        Switch to select calculation of etadot and Dps/Dt from continuity
        equation for diagnostic purposes (1) or not (0). Default value is 0.

    etapar : int
        GRIB parameter Id for etadot fields. Default value is 77.

    dpdeta : int
        Switch to select multiplication of etadot with dpdeta.
        Default value is 1.

    smooth : int
        Spectral truncation of ETADOT after calculation on Gaussian grid.
        Default value is 0.

    format : str
        The format of the GRIB data. Default value is 'GRIB1'.

    addpar : str
        List of additional surface level ECMWF parameter to be retrieved.
        Default value is None.

    prefix : str
        Prefix string for the final FLEXPART/FLEXTRA ready input files.
        Default value is 'EN'.

    cwc : int
        Switch to select wether the sum of cloud liquid water content and
        cloud ice water content should be retrieved. Default value is 0.

    wrf : int
        Switch to select further parameters for retrievment to support
        WRF simulations. Default value is 0.

    ecfsdir : str
        Path to the ECMWF storage  'ectmp:/${USER}/econdemand/'

    mailfail : list of str
        Email list for sending error log files from ECMWF servers.
        The email addresses should be seperated by a comma.
        Default value is ['${USER}'].

    mailops : list of str
        Email list for sending operational log files from ECMWF servers.
        The email addresses should be seperated by a comma.
        Default value is ['${USER}'].

    ecstorage : int
        Switch to select storage of FLEXPART ready output files
        in the ECFS file system. Default value is 0.

    ectrans : int
        Switch to select the transfer of FLEXPART ready output files
        to the gateway server. Default value is 0.

    inputdir : str
        Path to the temporary directory for the retrieval grib files and
        other processing files. Default value is _config.PATH_INPUT_DIR.

    outputdir : str
        Path to the final directory where the final FLEXPART ready input
        files are stored. Default value is None.

    flexextractdir : str
        Path to the flex_extract root directory. Default value is
        _config.PATH_FLEXEXTRACT_DIR.

    exedir : str
        Path to the FORTRAN executable file. Default value is
        _config.PATH_FORTRAN_SRC.

    installdir : str
        Path to a FLEXPART root directory. Default value is None.

    makefile : str
        Name of the makefile to be used for the Fortran program.
        Default value is None.

    destination : str
        The remote destination which is used to transfer files
        from ECMWF server to local gateway server. Default value is None.

    gateway : str
        The gateway server the user is using. Default value is None.

    ecuid : str
        The user id on ECMWF server. Default value is None.

    ecgid : str
        The group id on ECMWF server. Default value is None.

    install_target : str
        Defines the location where the installation is to be done.
        Default value is None.

    debug : int
        Switch to keep temporary files at the end of postprocessing (1) or
        to delete all temporary files except the final output files (0).
        Default value is 0.

    oper : int
        Switch to prepare the operational job script. Start date, end date and
        basetime will be prepared with environment variables.
        Default value is 0.

    request : int
        Switch to select between just retrieving the data (0), writing the mars
        parameter values to a csv file (1) or doing both (2).
        Default value is 0.

    public : int
        Switch to select kind of ECMWF Web Api access and the
        possible data sets. Public data sets (1) and Memberstate data sets (0).
        Default value is 0.

    ec_api : boolean
        Tells wether the ECMWF Web API was able to load or not.
        Default value is None.

    cds_api : boolean
        Tells wether the CDS API was able to load or not.
        Default value is None.

    purefc : int
        Switch to decide wether the job is a pure forecast retrieval or
        coupled with analysis data. Default value is 0.

    rrint : int
        Switch to select between old precipitation disaggregation method (0)
        or the new IA3 disaggegration method (1). Default value is 0.

    doubleelda : int
        Switch to select the calculation of extra ensemble members for the
        ELDA stream. It doubles the amount of retrieved ensemble members.

    logicals : list of str
        List of the names of logical switches which controls the flow
        of the program. Default list is ['gauss', 'omega', 'omegadiff', 'eta',
        'etadiff', 'dpdeta', 'cwc', 'wrf', 'ecstorage',
        'ectrans', 'debug', 'request', 'public', 'purefc', 'rrint', 'doubleelda']
    '''

    def __init__(self, filename):
        '''Initialises the instance of ControlFile class and defines
        all class attributes with default values. Afterwards calls
        function __read_controlfile__ to read parameter from Control file.

        Parameters
        ----------
        filename : str
            Name of CONTROL file.

        Return
        ------

        '''

        # list of all possible class attributes and their default values
        self.controlfile = filename
        self.start_date = None
        self.end_date = None
        self.date_chunk = 3
        self.job_chunk = None
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
        self.ecstorage = 0
        self.ectrans = 0
        self.inputdir = _config.PATH_INPUT_DIR
        self.outputdir = None
        self.flexextractdir = _config.PATH_FLEXEXTRACT_DIR
        self.exedir = _config.PATH_FORTRAN_SRC
        self.installdir = None
        self.makefile = None
        self.destination = None
        self.gateway = None
        self.ecuid = None
        self.ecgid = None
        self.install_target = None
        self.debug = 0
        self.oper = 0
        self.request = 0
        self.public = 0
        self.ec_api = None
        self.cds_api = None
        self.purefc = 0
        self.rrint = 0
        self.doubleelda = 0

        self.logicals = ['gauss', 'omega', 'omegadiff', 'eta', 'etadiff',
                         'dpdeta', 'cwc', 'wrf', 'ecstorage',
                         'ectrans', 'debug', 'oper', 'request', 'public',
                         'purefc', 'rrint', 'doubleelda']

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
                                my_error('Could not find variable '
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
        args : Namespace
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
        for k, v in arguments.items():
            setattr(self, str(k), v)

        return

    def assign_envs_to_control(self, envs):
        '''Assigns the ECMWF environment parameter.

        Parameters
        ----------
        envs : dict of str
            Contains the ECMWF environment parameternames "ECUID", "ECGID",
            "DESTINATION" and "GATEWAY" with its corresponding values.
            They were read from the file "ECMWF_ENV".

        Return
        ------

        '''

        for k, v in envs.items():
            setattr(self, str(k).lower(), str(v))

        return

    def check_conditions(self, queue):
        '''Checks a couple of necessary attributes and conditions,
        such as if they exist and contain values.
        Otherwise set default values.

        Parameters
        ----------
        queue : str
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

        self.outputdir, self.installdir = check_pathes(self.inputdir,
                                                       self.outputdir,
                                                       self.installdir,
                                                       self.flexextractdir)

        self.start_date, self.end_date = check_dates(self.start_date,
                                                     self.end_date)

        self.basetime = check_basetime(self.basetime)

        self.levelist, self.level = check_levels(self.levelist, self.level)

        self.step = check_step(self.step)

        self.maxstep = check_maxstep(self.maxstep, self.step)

        check_request(self.request,
                      os.path.join(self.inputdir, _config.FILE_MARS_REQUESTS))

        check_public(self.public, self.dataset, self.marsclass)

        self.type = check_type(self.type, self.step)

        self.time = check_time(self.time)

        self.purefc = check_purefc(self.type)

        self.type, self.time, self.step = check_len_type_time_step(self.type,
                                                                   self.time,
                                                                   self.step,
                                                                   self.maxstep,
                                                                   self.purefc)

        self.acctype = check_acctype(self.acctype, self.type)

        self.acctime = check_acctime(self.acctime, self.marsclass,
                                     self.purefc, self.time)

        self.accmaxstep = check_accmaxstep(self.accmaxstep, self.marsclass,
                                           self.purefc, self.maxstep)

        self.grid = check_grid(self.grid)

        self.area = check_area(self.grid, self.area, self.upper, self.lower,
                               self.left, self.right)

        self.addpar = check_addpar(self.addpar)

        self.job_chunk = check_job_chunk(self.job_chunk)

        self.number = check_number(self.number)

        return

    def to_list(self):
        '''Just generates a list of strings containing the attributes and
        assigned values except the attributes "_expanded", "exedir",
        "flexextractdir" and "installdir".

        Parameters
        ----------

        Return
        ------
        l : list of *
            A sorted list of the all ControlFile class attributes with
            their values except the attributes "_expanded", "exedir",
            "flexextractdir" and "installdir".
        '''

        import collections

        attrs = collections.OrderedDict(sorted(vars(self).copy().items()))

        l = list()

        for item in attrs.items():
            if '_expanded' in item[0]:
                pass
            elif 'exedir' in item[0]:
                pass
            elif 'installdir' in item[0]:
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
