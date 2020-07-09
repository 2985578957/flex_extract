#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - extended with class Control
#        - removed functions mkdir_p, daterange, years_between, months_between
#        - added functions darain, dapoly, to_param_id, init128, normal_exit,
#          my_error, clean_up, install_args_and_control,
#          interpret_args_and_control,
#        - removed function __del__ in class EIFLexpart
#        - added the following functions in EIFlexpart:
#            - create_namelist
#            - process_output
#            - deacc_fluxes
#        - modified existing EIFlexpart - functions for the use in
#          flex_extract
#        - retrieve also longer term forecasts, not only analyses and
#          short term forecast data
#        - added conversion into GRIB2
#
#    February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - removed function getFlexpartTime in class EcFlexpart
#        - outsourced class ControlFile
#        - outsourced class MarsRetrieval
#        - changed class name from EIFlexpart to EcFlexpart
#        - applied minor code changes (style)
#        - removed "dead code" , e.g. retrieval of Q since it is not needed
#        - removed "times" parameter from retrieve-method since it is not used
#        - seperated function "retrieve" into smaller functions (less code
#          duplication, easier testing)
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
#pylint: disable=unsupported-assignment-operation
# this is disabled because for this specific case its an error in pylint
#pylint: disable=consider-using-enumerate
# this is not useful in this case
#pylint: disable=unsubscriptable-object
# this error is a bug
#pylint: disable=ungrouped-imports
# not necessary that we group the imports
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
from __future__ import print_function

import os
import sys
import glob
import shutil
from datetime import datetime, timedelta

# software specific classes and modules from flex_extract
#pylint: disable=wrong-import-position
sys.path.append('../')
import _config
from Classes.GribUtil import GribUtil
from Mods.tools import (init128, to_param_id, silent_remove, product,
                        my_error, get_informations, get_dimensions,
                        execute_subprocess, to_param_id_with_tablenumber,
                        generate_retrieval_period_boundary)
from Classes.MarsRetrieval import MarsRetrieval
from Classes.UioFiles import UioFiles
import Mods.disaggregation as disaggregation
#pylint: enable=wrong-import-position
# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class EcFlexpart(object):
    '''
    Class to represent FLEXPART specific ECMWF data.

    FLEXPART needs grib files in a specifc format. All necessary data fields
    for one time step are stored in a single file. The class represents an
    instance with all the parameter and settings necessary for retrieving
    MARS data and modifing them so they are fitting FLEXPART needs. The class
    is able to disaggregate the fluxes and convert grid types to the one needed
    by FLEXPART, therefore using the FORTRAN program.

    Attributes
    ----------
    mreq_count : int
        Counter for the number of generated mars requests.

    inputdir : str
        Path to the directory where the retrieved data is stored.

    dataset : str
        For public datasets there is the specific naming and parameter
        dataset which has to be used to characterize the type of
        data.

    basetime : int
        The time for a half day retrieval. The 12 hours upfront are to be
        retrieved.

    dtime : str
        Time step in hours.

    acctype : str
        The field type for the accumulated forecast fields.

    acctime : str
        The starting time from the accumulated forecasts.

    accmaxstep : str
        The maximum forecast step for the accumulated forecast fields.

    marsclass : str
        Characterisation of dataset.

    stream : str
        Identifies the forecasting system used to generate the data.

    number : str
        Selects the member in ensemble forecast run.

    resol : str
        Specifies the desired triangular truncation of retrieved data,
        before carrying out any other selected post-processing.

    accuracy : str
        Specifies the number of bits per value to be used in the
        generated GRIB coded fields.

    addpar : str
        List of additional parameters to be retrieved.

    level : str
        Specifies the maximum level.

    expver : str
        The version of the dataset.

    levelist : str
        Specifies the required levels.

    glevelist : str
        Specifies the required levels for gaussian grids.

    gaussian : str
        This parameter is deprecated and should no longer be used.
        Specifies the desired type of Gaussian grid for the output.

    grid : str
        Specifies the output grid which can be either a Gaussian grid
        or a Latitude/Longitude grid.

    area : str
        Specifies the desired sub-area of data to be extracted.

    purefc : int
        Switch for definition of pure forecast mode or not.

    outputfilelist : list of str
        The final list of FLEXPART ready input files.

    types : dictionary
        Determines the combination of type of fields, time and forecast step
        to be retrieved.

    params : dictionary
        Collection of grid types and their corresponding parameters,
        levels, level types and the grid definition.

    server : ECMWFService or ECMWFDataServer
        This is the connection to the ECMWF data servers.

    public : int
        Decides which Web API Server version is used.

    dates : str
        Contains start and end date of the retrieval in the format
        "YYYYMMDD/to/YYYYMMDD"
    '''

    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, c, fluxes=False):
        '''Creates an object/instance of EcFlexpart with the associated
        settings of its attributes for the retrieval.

        Parameters:
        -----------
        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        fluxes : boolean, optional
            Decides if the flux parameter settings are stored or
            the rest of the parameter list.
            Default value is False.

        Return
        ------

        '''
        # set a counter for the number of generated mars requests
        self.mreq_count = 0

        self.inputdir = c.inputdir
        self.dataset = c.dataset
        self.basetime = c.basetime
        self.dtime = c.dtime
        self.acctype = c.acctype
        self.acctime = c.acctime
        self.accmaxstep = c.accmaxstep
        self.marsclass = c.marsclass
        self.stream = c.stream
        self.number = c.number
        self.resol = c.resol
        self.accuracy = c.accuracy
        self.addpar = c.addpar
        self.level = c.level
        self.expver = c.expver
        self.levelist = c.levelist
        self.glevelist = '1/to/' + c.level # in case of gaussian grid
        self.gaussian = c.gaussian
        self.grid = c.grid
        self.area = c.area
        self.purefc = c.purefc
        self.outputfilelist = []

        # Define the different types of field combinations (type, time, step)
        self.types = {}
        # Define the parameters and their level types, level list and
        # grid resolution for the retrieval job
        self.params = {}

        if fluxes:
            self._create_params_fluxes()
        else:
            self._create_params(c.gauss, c.eta, c.omega, c.cwc, c.wrf)

        if fluxes:# and not c.purefc:
            self._create_field_types_fluxes()
        else:
            self._create_field_types(c.type, c.time, c.step)
        return

    def _create_field_types(self, ftype, ftime, fstep):
        '''Create the combination of field type, time and forecast step.

        Parameters:
        -----------
        ftype : list of str
            List of field types.

        ftime : list of str
            The time in hours of the field.

        fstep : str
            Specifies the forecast time step from forecast base time.
            Valid values are hours (HH) from forecast base time.

        Return
        ------

        '''
        i = 0
        for ty, st, ti in zip(ftype, fstep, ftime):
            btlist = list(range(len(ftime)))
            if self.basetime == 12:
                btlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            if self.basetime == 0:
                btlist = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0]

            # if ((ty.upper() == 'AN' and (int(c.time[i]) % int(c.dtime)) == 0) or
                # (ty.upper() != 'AN' and (int(c.step[i]) % int(c.dtime)) == 0 and
                 # (int(c.step[i]) % int(c.dtime) == 0)) ) and \
                 # (int(c.time[i]) in btlist or c.purefc):

            if (i in btlist) or self.purefc:

                if ((ty.upper() == 'AN' and (int(ti) % int(self.dtime)) == 0) or
                    (ty.upper() != 'AN' and (int(st) % int(self.dtime)) == 0)):

                    if ty not in self.types.keys():
                        self.types[ty] = {'times': '', 'steps': ''}

                    if ti not in self.types[ty]['times']:
                        if self.types[ty]['times']:
                            self.types[ty]['times'] += '/'
                        self.types[ty]['times'] += ti

                    if st not in self.types[ty]['steps']:
                        if self.types[ty]['steps']:
                            self.types[ty]['steps'] += '/'
                        self.types[ty]['steps'] += st
            i += 1

        return

    def _create_field_types_fluxes(self):
        '''Create the combination of field type, time and forecast step
        for the flux data.

        Parameters:
        -----------

        Return
        ------

        '''
        if self.purefc:
            # need to retrieve forecasts for step 000 in case of pure forecast
            steps = '{}/to/{}/by/{}'.format(0, self.accmaxstep, self.dtime)
        else:
            steps = '{}/to/{}/by/{}'.format(self.dtime,
                                            self.accmaxstep,
                                            self.dtime)

        self.types[str(self.acctype)] = {'times': str(self.acctime),
                                         'steps': steps}
        return

    def _create_params(self, gauss, eta, omega, cwc, wrf):
        '''Define the specific parameter settings for retrievment.

        The different parameters need specific grid types and level types
        for retrievement. We might get following combination of types
        (depending on selection and availability):
        (These are short cuts for the grib file names (leading sequence)
        SH__ML, OG__ML, GG__ML, SH__SL, OG__SL, GG__SL, OG_OROLSM_SL
        where:
            SH = Spherical Harmonics, GG = Gaussian Grid, OG = Output Grid,
            ML = Model Level, SL = Surface Level

        For each of this combination there is a list of parameter names,
        the level type, the level list and the grid resolution.

        There are different scenarios for data extraction from MARS:
        1) Retrieval of etadot
           eta=1, gauss=0, omega=0
        2) Calculation of etadot from divergence
           eta=0, gauss=1, omega=0
        3) Calculation of etadot from omega (for makes sense for debugging)
           eta=0, gauss=0, omega=1
        4) Retrieval and Calculation of etadot (only for debugging)
           eta=1, gauss=1, omega=0
        5) Download also specific model and surface level data for FLEXPART-WRF

        Parameters:
        -----------
        gauss : int
            Gaussian grid is retrieved.

        eta : int
            Etadot parameter will be directly retrieved.

        omega : int
            The omega paramterwill be retrieved.

        cwc : int
            The cloud liquid and ice water content will be retrieved.

        wrf : int
            Additional model level and surface level data will be retrieved for
            WRF/FLEXPART-WRF simulations.

        Return
        ------

        '''
        # SURFACE FIELDS
        #-----------------------------------------------------------------------
        self.params['SH__SL'] = ['LNSP', 'ML', '1', 'OFF']
        self.params['OG__SL'] = ['SD/MSL/TCC/10U/10V/2T/2D/Z/LSM', \
                                 'SFC', '1', self.grid]
        if self.addpar:
            self.params['OG__SL'][0] += self.addpar

        if self.marsclass.upper() == 'EA' or self.marsclass.upper() == 'EP':
            self.params['OG_OROLSM__SL'] = ["SDOR/CVL/CVH/FSR",
                                            'SFC', '1', self.grid]
        else:
            self.params['OG_OROLSM__SL'] = ["SDOR/CVL/CVH/SR", \
                                            'SFC', '1', self.grid]

        # MODEL LEVEL FIELDS
        #-----------------------------------------------------------------------
        self.params['OG__ML'] = ['T/Q', 'ML', self.levelist, self.grid]

        if not gauss and eta:
            self.params['OG__ML'][0] += '/U/V/ETADOT'
        elif gauss and not eta:
            self.params['GG__SL'] = ['Q', 'ML', '1',
                                     '{}'.format((int(self.resol) + 1) // 2)]
            self.params['SH__ML'] = ['U/V/D', 'ML', self.glevelist, 'OFF']
        elif not gauss and not eta:
            self.params['OG__ML'][0] += '/U/V'
        else:  # GAUSS and ETA
            print('Warning: Collecting etadot and parameters for gaussian grid '
                  'is a very costly parameter combination, '
                  'use this combination only for debugging!')
            self.params['GG__SL'] = ['Q', 'ML', '1',
                                     '{}'.format((int(self.resol) + 1) // 2)]
            self.params['GG__ML'] = ['U/V/D/ETADOT', 'ML', self.glevelist,
                                     '{}'.format((int(self.resol) + 1) // 2)]

        if omega:
            self.params['OG__ML'][0] += '/W'

        if cwc:
            self.params['OG__ML'][0] += '/CLWC/CIWC'

        # ADDITIONAL FIELDS FOR FLEXPART-WRF MODEL (IF QUESTIONED)
        # ----------------------------------------------------------------------
        if wrf:
            # @WRF
            # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
            #
            # UNDER CONSTRUCTION !!!
            #

            print('WRF VERSION IS UNDER CONSTRUCTION!') # dummy argument

            #self.params['OG__ML'][0] += '/Z/VO'
            #if '/D' not in self.params['OG__ML'][0]:
            #    self.params['OG__ML'][0] += '/D'

            #wrf_sfc = ['SP','SKT','SST','CI','STL1','STL2', 'STL3','STL4',
            #           'SWVL1','SWVL2','SWVL3','SWVL4']
            #for par in wrf_sfc:
            #    if par not in self.params['OG__SL'][0]:
            #        self.params['OG__SL'][0] += '/' + par

        return


    def _create_params_fluxes(self):
        '''Define the parameter setting for flux data.

        Flux data are accumulated fields in time and are stored on the
        surface level. The leading short cut name for the grib files is:
        "OG_acc_SL" with OG for Regular Output Grid, SL for Surface Level, and
        acc for Accumulated Grid.
        The params dictionary stores a list of parameter names, the level type,
        the level list and the grid resolution.

        The flux data are: LSP/CP/SSHF/EWSS/NSSS/SSR

        Parameters:
        -----------

        Return
        ------

        '''
        self.params['OG_acc_SL'] = ["LSP/CP/SSHF/EWSS/NSSS/SSR",
                                    'SFC', '1', self.grid]
        return


    def _mk_targetname(self, ftype, param, date):
        '''Creates the filename for the requested grib data to be stored in.
        This name is passed as the "target" parameter in the request.

        Parameters
        ----------
        ftype : str
            Shortcut name of the type of the field. E.g. AN, FC, PF, ...

        param : str
            Shortcut of the grid type. E.g. SH__ML, SH__SL, GG__ML,
            GG__SL, OG__ML, OG__SL, OG_OROLSM_SL, OG_acc_SL

        date : str
            The date period of the grib data to be stored in this file.

        Return
        ------
        targetname : str
            The target filename for the grib data.
        '''
        targetname = (self.inputdir + '/' + ftype + param + '.' + date + '.' +
                      str(os.getppid()) + '.' + str(os.getpid()) + '.grb')

        return targetname


    def _start_retrievement(self, request, par_dict):
        '''Creates the Mars Retrieval and prints or submits the request
        depending on the status of the request variable.

        Parameters
        ----------
        request : int
            Selects the mode of retrieval.
            0: Retrieves the data from ECMWF.
            1: Prints the mars requests to an output file.
            2: Retrieves the data and prints the mars request.

        par_dict : dictionary
            Contains all parameter which have to be set for creating the
            Mars Retrievals. The parameter are:
            marsclass, dataset, stream, type, levtype, levelist, resol,
            gaussian, accuracy, grid, target, area, date, time, number,
            step, expver, param

        Return
        ------

        '''
        # increase number of mars requests
        self.mreq_count += 1

        MR = MarsRetrieval(self.server,
                           self.public,
                           marsclass=par_dict['marsclass'],
                           dataset=par_dict['dataset'],
                           stream=par_dict['stream'],
                           type=par_dict['type'],
                           levtype=par_dict['levtype'],
                           levelist=par_dict['levelist'],
                           resol=par_dict['resol'],
                           gaussian=par_dict['gaussian'],
                           accuracy=par_dict['accuracy'],
                           grid=par_dict['grid'],
                           target=par_dict['target'],
                           area=par_dict['area'],
                           date=par_dict['date'],
                           time=par_dict['time'],
                           number=par_dict['number'],
                           step=par_dict['step'],
                           expver=par_dict['expver'],
                           param=par_dict['param'])

        if request == 0:
            MR.display_info()
            MR.data_retrieve()
        elif request == 1:
            MR.print_infodata_csv(self.inputdir, self.mreq_count)
        elif request == 2:
            MR.print_infodata_csv(self.inputdir, self.mreq_count)
            MR.display_info()
            MR.data_retrieve()
        else:
            print('Failure')

        return


    def _mk_index_values(self, inputdir, inputfiles, keys):
        '''Creates an index file for a set of grib parameter keys.
        The values from the index keys are returned in a list.

        Parameters
        ----------
        keys : dictionary
            List of parameter names which serves as index.

        inputfiles : UioFiles
            Contains a list of files.

        Return
        ------
        iid : codes_index
            This is a grib specific index structure to access
            messages in a file.

        index_vals : list of list  of str
            Contains the values from the keys used for a distinct selection
            of grib messages in processing  the grib files.
            Content looks like e.g.:
            index_vals[0]: ('20171106', '20171107', '20171108') ; date
            index_vals[1]: ('0', '1200', '1800', '600') ; time
            index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange
        '''
        from eccodes import codes_index_get

        iid = None
        index_keys = keys

        indexfile = os.path.join(inputdir, _config.FILE_GRIB_INDEX)
        silent_remove(indexfile)
        grib = GribUtil(inputfiles.files)
        # creates new index file
        iid = grib.index(index_keys=index_keys, index_file=indexfile)

        # read the values of index keys
        index_vals = []
        for key in index_keys:
            key_vals = codes_index_get(iid, key)
            # have to sort the key values for correct order,
            # therefore convert to int first
            key_vals = [int(k) for k in key_vals]
            key_vals.sort()
            key_vals = [str(k) for k in key_vals]
            index_vals.append(key_vals)
            # index_vals looks for example like:
            # index_vals[0]: ('20171106', '20171107', '20171108') ; date
            # index_vals[1]: ('0', '1200') ; time
            # index_vals[2]: (3', '6', '9', '12') ; stepRange

        return iid, index_vals


    def retrieve(self, server, dates, public, request, inputdir='.'):
        '''Finalizing the retrieval information by setting final details
        depending on grid type.
        Prepares MARS retrievals per grid type and submits them.

        Parameters
        ----------
        server : ECMWFService or ECMWFDataServer
            The connection to the ECMWF server. This is different
            for member state users which have full access and non
            member state users which have only access to the public
            data sets. The decision is made from command line argument
            "public"; for public access its True (ECMWFDataServer)
            for member state users its False (ECMWFService)

        dates : str
            Contains start and end date of the retrieval in the format
            "YYYYMMDD/to/YYYYMMDD"

        request : int
            Selects the mode of retrieval.
            0: Retrieves the data from ECMWF.
            1: Prints the mars requests to an output file.
            2: Retrieves the data and prints the mars request.

        inputdir : str, optional
            Path to the directory where the retrieved data is about
            to be stored. The default is the current directory ('.').

        Return
        ------

        '''
        self.dates = dates
        self.server = server
        self.public = public
        self.inputdir = inputdir
        oro = False

        # define times with datetime module
        t12h = timedelta(hours=12)
        t24h = timedelta(hours=24)

        # dictionary which contains all parameter for the mars request,
        # entries with a "None" will change in different requests and will
        # therefore be set in each request seperately
        retr_param_dict = {'marsclass':self.marsclass,
                           'dataset':self.dataset,
                           'stream':None,
                           'type':None,
                           'levtype':None,
                           'levelist':None,
                           'resol':self.resol,
                           'gaussian':None,
                           'accuracy':self.accuracy,
                           'grid':None,
                           'target':None,
                           'area':None,
                           'date':None,
                           'time':None,
                           'number':self.number,
                           'step':None,
                           'expver':self.expver,
                           'param':None}

        for ftype in sorted(self.types):
            # ftype contains field types such as
            #     [AN, FC, PF, CV]
            for pk, pv in sorted(self.params.items()):
                # pk contains one of these keys of params
                #     [SH__ML, SH__SL, GG__ML, GG__SL, OG__ML, OG__SL,
                #      OG_OROLSM_SL, OG_acc_SL]
                # pv contains all of the items of the belonging key
                #     [param, levtype, levelist, grid]
                if isinstance(pv, str):
                    continue
                retr_param_dict['type'] = ftype
                retr_param_dict['time'] = self.types[ftype]['times']
                retr_param_dict['step'] = self.types[ftype]['steps']
                retr_param_dict['date'] = self.dates
                retr_param_dict['stream'] = self.stream
                retr_param_dict['target'] = \
                    self._mk_targetname(ftype,
                                        pk,
                                        retr_param_dict['date'].split('/')[0])
                table128 = init128(_config.PATH_GRIBTABLE)
                ids = to_param_id_with_tablenumber(pv[0], table128)
                retr_param_dict['param'] = ids
                retr_param_dict['levtype'] = pv[1]
                retr_param_dict['levelist'] = pv[2]
                retr_param_dict['grid'] = pv[3]
                retr_param_dict['area'] = self.area
                retr_param_dict['gaussian'] = self.gaussian

                if pk == 'OG_OROLSM__SL' and not oro:
                    oro = True
                    # in CERA20C (class EP) there is no stream "OPER"!
                    if self.marsclass.upper() != 'EP':
                        retr_param_dict['stream'] = 'OPER'
                    retr_param_dict['type'] = 'AN'
                    retr_param_dict['time'] = '00'
                    retr_param_dict['step'] = '000'
                    retr_param_dict['date'] = self.dates.split('/')[0]
                    retr_param_dict['target'] = self._mk_targetname('',
                                                                    pk,
                                                                    retr_param_dict['date'])
                elif pk == 'OG_OROLSM__SL' and oro:
                    continue
                if pk == 'GG__SL' and pv[0] == 'Q':
                    retr_param_dict['area'] = ""
                    retr_param_dict['gaussian'] = 'reduced'
                if ftype.upper() == 'FC' and \
                    'acc' not in retr_param_dict['target']:
                    if (int(retr_param_dict['time'][0]) +
                        int(retr_param_dict['step'][0])) > 23:
                        dates = retr_param_dict['date'].split('/')
                        sdate = datetime.strptime(dates[0], '%Y%m%d%H')
                        sdate = sdate - timedelta(days=1)
                        retr_param_dict['date'] = '/'.join(
                            [sdate.strftime("%Y%m%d")] +
                            retr_param_dict['date'][1:])

                        print('CHANGED FC start date to ' +
                              sdate.strftime("%Y%m%d") +
                              ' to accomodate TIME=' +
                              retr_param_dict['time'][0] +
                              ', STEP=' +
                              retr_param_dict['time'][0])

    # ------  on demand path  --------------------------------------------------
                if self.basetime is None:
                    # ******* start retrievement
                    self._start_retrievement(request, retr_param_dict)
    # ------  operational path  ------------------------------------------------
                else:
                    # check if mars job requests fields beyond basetime.
                    # if yes eliminate those fields since they may not
                    # be accessible with user's credentials

                    enddate = retr_param_dict['date'].split('/')[-1]
                    elimit = datetime.strptime(enddate + str(self.basetime),
                                               '%Y%m%d%H')

                    if self.basetime == 12:
                        # --------------  flux data ----------------------------
                        if 'acc' in pk:
                            startdate = retr_param_dict['date'].split('/')[0]
                            enddate = datetime.strftime(elimit - t24h, '%Y%m%d')
                            retr_param_dict['date'] = '/'.join([startdate,
                                                                'to',
                                                                enddate])

                            # ******* start retrievement
                            self._start_retrievement(request, retr_param_dict)

                            retr_param_dict['date'] = \
                                datetime.strftime(elimit - t12h, '%Y%m%d')
                            retr_param_dict['time'] = '00'
                            retr_param_dict['target'] = \
                                self._mk_targetname(ftype, pk,
                                                    retr_param_dict['date'])

                            # ******* start retrievement
                            self._start_retrievement(request, retr_param_dict)

                        # --------------  non flux data ------------------------
                        else:
                            # ******* start retrievement
                            self._start_retrievement(request, retr_param_dict)

                    elif self.basetime == 0:
#                        retr_param_dict['date'] = \
#                            datetime.strftime(elimit - t24h, '%Y%m%d')

                        timesave = ''.join(retr_param_dict['time'])

                        if all(['/' in retr_param_dict['time'],
                                pk != 'OG_OROLSM__SL',
                                'acc' not in pk]):
                            times = retr_param_dict['time'].split('/')
                            steps = retr_param_dict['step'].split('/')

                            while int(times[0]) + int(steps[0]) <= 12:
                                times = times[1:]
                                if len(times) > 1:
                                    retr_param_dict['time'] = '/'.join(times)
                                else:
                                    retr_param_dict['time'] = times[0]

                        if all([pk != 'OG_OROLSM__SL',
                                int(retr_param_dict['step'].split('/')[0]) == 0,
                                int(timesave.split('/')[0]) == 0]):

                            retr_param_dict['date'] = \
                                datetime.strftime(elimit, '%Y%m%d')
                            retr_param_dict['time'] = '00'
                            retr_param_dict['step'] = '000'
                            retr_param_dict['target'] = \
                                self._mk_targetname(ftype, pk,
                                                    retr_param_dict['date'])

                        # ******* start retrievement
                        self._start_retrievement(request, retr_param_dict)
                    else:
                        raise ValueError('ERROR: Basetime has an invalid value '
                                         '-> {}'.format(str(self.basetime)))

        if request == 0 or request == 2:
            print('MARS retrieve done ... ')
        elif request == 1:
            print('MARS request printed ...')

        return


    def write_namelist(self, c):
        '''Creates a namelist file in the temporary directory and writes
        the following values to it: maxl, maxb, mlevel,
        mlevelist, mnauf, metapar, rlo0, rlo1, rla0, rla1,
        momega, momegadiff, mgauss, msmooth, meta, metadiff, mdpdeta

        Parameters
        ----------
        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        filename : str
                Name of the namelist file.

        Return
        ------

        '''

        from genshi.template.text import NewTextTemplate
        from genshi.template import  TemplateLoader
        from genshi.template.eval import  UndefinedError
        import numpy as np

        try:
            loader = TemplateLoader(_config.PATH_TEMPLATES, auto_reload=False)
            namelist_template = loader.load(_config.TEMPFILE_NAMELIST,
                                            cls=NewTextTemplate)

            self.inputdir = c.inputdir
            area = np.asarray(self.area.split('/')).astype(float)
            grid = np.asarray(self.grid.split('/')).astype(float)

            if area[1] > area[3]:
                area[1] -= 360
            maxl = int(round((area[3] - area[1]) / grid[1])) + 1
            maxb = int(round((area[0] - area[2]) / grid[0])) + 1

            stream = namelist_template.generate(
                maxl=str(maxl),
                maxb=str(maxb),
                mlevel=str(self.level),
                mlevelist=str(self.levelist),
                mnauf=str(self.resol),
                metapar='77',
                rlo0=str(area[1]),
                rlo1=str(area[3]),
                rla0=str(area[2]),
                rla1=str(area[0]),
                momega=str(c.omega),
                momegadiff=str(c.omegadiff),
                mgauss=str(c.gauss),
                msmooth=str(c.smooth),
                meta=str(c.eta),
                metadiff=str(c.etadiff),
                mdpdeta=str(c.dpdeta)
            )
        except UndefinedError as e:
            print('... ERROR ' + str(e))

            sys.exit('\n... error occured while trying to generate namelist ' +
                     _config.TEMPFILE_NAMELIST)
        except OSError as e:
            print('... ERROR CODE: ' + str(e.errno))
            print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

            sys.exit('\n... error occured while trying to generate template ' +
                     _config.TEMPFILE_NAMELIST)

        try:
            namelistfile = os.path.join(self.inputdir, _config.FILE_NAMELIST)

            with open(namelistfile, 'w') as f:
                f.write(stream.render('text'))
        except OSError as e:
            print('... ERROR CODE: ' + str(e.errno))
            print('... ERROR MESSAGE:\n \t ' + str(e.strerror))

            sys.exit('\n... error occured while trying to write ' +
                     namelistfile)

        return


    def deacc_fluxes(self, inputfiles, c):
        '''De-accumulate and disaggregate flux data.

        Goes through all flux fields in ordered time and de-accumulate
        the fields. Afterwards the fields are disaggregated in time.
        Different versions of disaggregation is provided for rainfall
        data (darain, modified linear) and the surface fluxes and
        stress data (dapoly, cubic polynomial).

        Parameters
        ----------
        inputfiles : UioFiles
            Contains the list of files that contain flux data.

        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        Return
        ------

        '''
        import numpy as np
        from eccodes import (codes_index_select, codes_get,
                             codes_get_values, codes_set_values, codes_set,
                             codes_write, codes_release, codes_new_from_index,
                             codes_index_release)

        table128 = init128(_config.PATH_GRIBTABLE)
        # get ids from the flux parameter names
        pars = to_param_id(self.params['OG_acc_SL'][0], table128)

        iid = None
        index_vals = None

        # get the values of the keys which are used for distinct access
        # of grib messages via product and save the maximum number of
        # ensemble members if there is more than one
        if '/' in self.number:
            # more than one ensemble member is selected
            index_keys = ["number", "date", "time", "step"]
            # maximum ensemble number retrieved
            # + 1 for the control run (ensemble number 0)
            maxnum = int(self.number.split('/')[-1]) + 1
            # remember the index of the number values
            index_number = index_keys.index('number')
            # empty set to save ensemble numbers which were already processed
            ens_numbers = set()
            # index for the ensemble number
            inumb = 0
        else:
            index_keys = ["date", "time", "step"]
            # maximum ensemble number
            maxnum = None

        # get sorted lists of the index values
        # this is very important for disaggregating
        # the flux data in correct order
        iid, index_vals = self._mk_index_values(c.inputdir,
                                                inputfiles,
                                                index_keys)
        # index_vals looks like e.g.:
        # index_vals[0]: ('20171106', '20171107', '20171108') ; date
        # index_vals[1]: ('0', '600', '1200', '1800') ; time
        # index_vals[2]: ('0', '3', '6', '9', '12') ; stepRange

        if c.rrint:
            # set start and end timestamps for retrieval period
            if not c.purefc:
                start_date = datetime.strptime(c.start_date + '00', '%Y%m%d%H')
                end_date = datetime.strptime(c.end_date + '23', '%Y%m%d%H')
            else:
                sdate_str = c.start_date + '{:0>2}'.format(index_vals[1][0])
                start_date = datetime.strptime(sdate_str, '%Y%m%d%H')
                edate_str = c.end_date + '{:0>2}'.format(index_vals[1][-1])
                end_date = datetime.strptime(edate_str, '%Y%m%d%H')
                end_date = end_date + timedelta(hours=c.maxstep)

            # get necessary grid dimensions from grib files for storing the
            # precipitation fields
            info = get_informations(os.path.join(c.inputdir,
                                                 inputfiles.files[0]))
            dims = get_dimensions(info, c.purefc, c.dtime, index_vals,
                                  start_date, end_date)

            # create empty numpy arrays
            if not maxnum:
                lsp_np = np.zeros((dims[1] * dims[0], dims[2]), dtype=np.float64)
                cp_np = np.zeros((dims[1] * dims[0], dims[2]), dtype=np.float64)
            else:
                lsp_np = np.zeros((maxnum, dims[1] * dims[0], dims[2]), dtype=np.float64)
                cp_np = np.zeros((maxnum, dims[1] * dims[0], dims[2]), dtype=np.float64)

            # index counter for time line
            it_lsp = 0
            it_cp = 0

            # store the order of date and step
            date_list = []
            step_list = []

        # initialize dictionaries to store flux values per parameter
        orig_vals = {}
        deac_vals = {}
        for p in pars:
            orig_vals[p] = []
            deac_vals[p] = []

        # "product" genereates each possible combination between the
        # values of the index keys
        for prod in product(*index_vals):
            # e.g. prod = ('20170505', '0', '12')
            #             ( date     ,time, step)

            print('CURRENT PRODUCT: ', prod)

            # the whole process has to be done for each seperate ensemble member
            # therefore, for each new ensemble member we delete old flux values
            # and start collecting flux data from the beginning time step
            if maxnum and prod[index_number] not in ens_numbers:
                ens_numbers.add(prod[index_number])
                inumb = len(ens_numbers) - 1
                # re-initialize dictionaries to store flux values per parameter
                # for the next ensemble member
                it_lsp = 0
                it_cp = 0
                orig_vals = {}
                deac_vals = {}
                for p in pars:
                    orig_vals[p] = []
                    deac_vals[p] = []

            for i in range(len(index_keys)):
                codes_index_select(iid, index_keys[i], prod[i])

            # get first id from current product
            gid = codes_new_from_index(iid)

            # if there is no data for this specific time combination / product
            # skip the rest of the for loop and start with next timestep/product
            if not gid:
                continue

            # create correct timestamp from the three time informations
            cdate = str(codes_get(gid, 'date'))
            time = codes_get(gid, 'time') // 100  # integer
            step = codes_get(gid, 'step') # integer
            ctime = '{:0>2}'.format(time)

            t_date = datetime.strptime(cdate + ctime, '%Y%m%d%H')
            t_dt = t_date + timedelta(hours=step)
            t_m1dt = t_date + timedelta(hours=step-int(c.dtime))
            t_m2dt = t_date + timedelta(hours=step-2*int(c.dtime))
            if c.basetime is not None:
                t_enddate = datetime.strptime(c.end_date + str(c.basetime),
                                              '%Y%m%d%H')
            else:
                t_enddate = t_date + timedelta(2*int(c.dtime))

            # if necessary, add ensemble member number to filename suffix
            # otherwise, add empty string
            if maxnum:
                numbersuffix = '.N{:0>3}'.format(int(prod[index_number]))
            else:
                numbersuffix = ''

            if c.purefc:
                fnout = os.path.join(c.inputdir, 'flux' +
                                     t_date.strftime('%Y%m%d.%H') +
                                     '.{:0>3}'.format(step-2*int(c.dtime)) +
                                     numbersuffix)
                gnout = os.path.join(c.inputdir, 'flux' +
                                     t_date.strftime('%Y%m%d.%H') +
                                     '.{:0>3}'.format(step-int(c.dtime)) +
                                     numbersuffix)
                hnout = os.path.join(c.inputdir, 'flux' +
                                     t_date.strftime('%Y%m%d.%H') +
                                     '.{:0>3}'.format(step) +
                                     numbersuffix)
            else:
                fnout = os.path.join(c.inputdir, 'flux' +
                                     t_m2dt.strftime('%Y%m%d%H') + numbersuffix)
                gnout = os.path.join(c.inputdir, 'flux' +
                                     t_m1dt.strftime('%Y%m%d%H') + numbersuffix)
                hnout = os.path.join(c.inputdir, 'flux' +
                                     t_dt.strftime('%Y%m%d%H') + numbersuffix)

            print("outputfile = " + fnout)
            f_handle = open(fnout, 'wb')
            h_handle = open(hnout, 'wb')
            g_handle = open(gnout, 'wb')

            # read message for message and store relevant data fields, where
            # data keywords are stored in pars
            while True:
                if not gid:
                    break
                parId = codes_get(gid, 'paramId') # integer
                step = codes_get(gid, 'step') # integer
                time = codes_get(gid, 'time') # integer
                ni = codes_get(gid, 'Ni') # integer
                nj = codes_get(gid, 'Nj') # integer
                if parId not in orig_vals.keys():
                    # parameter is not a flux, find next one
                    continue

                # define conversion factor
                if parId == 142 or parId == 143:
                    fak = 1. / 1000.
                else:
                    fak = 3600.

                # get parameter values and reshape
                values = codes_get_values(gid)
                values = (np.reshape(values, (nj, ni))).flatten() / fak

                # save the original and accumulated values
                orig_vals[parId].append(values[:])

                if c.marsclass.upper() == 'EA' or step <= int(c.dtime):
                    # no de-accumulation needed
                    deac_vals[parId].append(values[:] / int(c.dtime))
                else:
                    # do de-accumulation
                    deac_vals[parId].append(
                        (orig_vals[parId][-1] - orig_vals[parId][-2]) /
                        int(c.dtime))

                # store precipitation if new disaggregation method is selected
                # only the exact days are needed
                if c.rrint:
                    if start_date <= t_dt <= end_date:
                        if not c.purefc:
                            if t_dt not in date_list:
                                date_list.append(t_dt)
                                step_list = [0]
                        else:
                            if t_date not in date_list:
                                date_list.append(t_date)
                            if step not in step_list:
                                step_list.append(step)
                        # store precipitation values
                        if maxnum and parId == 142:
                            lsp_np[inumb, :, it_lsp] = deac_vals[parId][-1][:]
                            it_lsp += 1
                        elif not maxnum and parId == 142:
                            lsp_np[:, it_lsp] = deac_vals[parId][-1][:]
                            it_lsp += 1
                        elif maxnum and parId == 143:
                            cp_np[inumb, :, it_cp] = deac_vals[parId][-1][:]
                            it_cp += 1
                        elif not maxnum and parId == 143:
                            cp_np[:, it_cp] = deac_vals[parId][-1][:]
                            it_cp += 1

                # information printout
                print(parId, time, step, len(values), values[0], np.std(values))

                # length of deac_vals[parId] corresponds to the
                # number of time steps, max. 4 are needed for disaggegration
                # with the old and original method
                # run over all grib messages and perform
                # shifting in time
                if len(deac_vals[parId]) >= 3:
                    if len(deac_vals[parId]) > 3:
                        if not c.rrint and (parId == 142 or parId == 143):
                            values = disaggregation.darain(deac_vals[parId])
                        else:
                            values = disaggregation.dapoly(deac_vals[parId])

                        if not (step == c.maxstep and c.purefc \
                                or t_dt == t_enddate):
                            # remove first time step in list to shift
                            # time line
                            orig_vals[parId].pop(0)
                            deac_vals[parId].pop(0)
                    else:
                        # if the third time step is read (per parId),
                        # write out the first one as a boundary value
                        if c.purefc:
                            values = deac_vals[parId][1]
                        else:
                            values = deac_vals[parId][0]

                    if not (c.rrint and (parId == 142 or parId == 143)):
                        codes_set_values(gid, values)

                        if c.purefc:
                            codes_set(gid, 'stepRange', max(0, step-2*int(c.dtime)))
                        else:
                            codes_set(gid, 'stepRange', 0)
                            codes_set(gid, 'time', t_m2dt.hour*100)
                            codes_set(gid, 'date', int(t_m2dt.strftime('%Y%m%d')))

                        codes_write(gid, f_handle)

                        # squeeze out information of last two steps
                        # contained in deac_vals[parId]
                        # Note that deac_vals[parId][0] has not been popped
                        # in this case

                        if step == c.maxstep and c.purefc or \
                           t_dt == t_enddate:
                            # last step
                            if c.purefc:
                                values = deac_vals[parId][3]
                                codes_set_values(gid, values)
                                codes_set(gid, 'stepRange', step)
                                #truedatetime = t_m2dt + timedelta(hours=2*int(c.dtime))
                                codes_write(gid, h_handle)
                            else:
                                values = deac_vals[parId][3]
                                codes_set_values(gid, values)
                                codes_set(gid, 'stepRange', 0)
                                truedatetime = t_m2dt + timedelta(hours=2*int(c.dtime))
                                codes_set(gid, 'time', truedatetime.hour * 100)
                                codes_set(gid, 'date', int(truedatetime.strftime('%Y%m%d')))
                                codes_write(gid, h_handle)

                            if parId == 142 or parId == 143:
                                values = disaggregation.darain(list(reversed(deac_vals[parId])))
                            else:
                                values = disaggregation.dapoly(list(reversed(deac_vals[parId])))

                            # step before last step
                            if c.purefc:
                                codes_set(gid, 'stepRange', step-int(c.dtime))
                                #truedatetime = t_m2dt + timedelta(hours=int(c.dtime))
                                codes_set_values(gid, values)
                                codes_write(gid, g_handle)
                            else:
                                codes_set(gid, 'stepRange', 0)
                                truedatetime = t_m2dt + timedelta(hours=int(c.dtime))
                                codes_set(gid, 'time', truedatetime.hour * 100)
                                codes_set(gid, 'date', int(truedatetime.strftime('%Y%m%d')))
                                codes_set_values(gid, values)
                                codes_write(gid, g_handle)

                codes_release(gid)

                gid = codes_new_from_index(iid)

            f_handle.close()
            g_handle.close()
            h_handle.close()

        codes_index_release(iid)

        if c.rrint:
            self._create_rr_grib_dummy(inputfiles.files[0], c.inputdir)

            self._prep_new_rrint(dims[0], dims[1], dims[2], lsp_np,
                                 cp_np, maxnum, index_keys, index_vals, c)

        return

    def _prep_new_rrint(self, ni, nj, nt, lsp_np, cp_np, maxnum, index_keys, index_vals, c):
        '''Calculates and writes out the disaggregated precipitation fields.

        Disaggregation is done in time and original times are written to the
        flux files, while the additional subgrid times are written to
        extra files output files. They are named like the original files with
        suffixes "_1" and "_2" for the first and second subgrid point.

        Parameters
        ----------
        ni : int
            Amount of zonal grid points.

        nj : int
            Amount of meridional grid points.

        nt : int
            Number of time steps.

        lsp_np : numpy array of float
            The large scale precipitation fields for each time step.
            Shape (ni * nj, nt).

        cp_np : numpy array of float
            The convective precipitation fields for each time step.
            Shape (ni * nj, nt).

        maxnum : int
            The maximum number of ensemble members. It is None
            if there are no or just one ensemble.

        index_keys : dictionary
            List of parameter names which serves as index.

        index_vals : list of list  of str
            Contains the values from the keys used for a distinct selection
            of grib messages in processing  the grib files.
            Content looks like e.g.:
            index_vals[0]: ('20171106', '20171107', '20171108') ; date
            index_vals[1]: ('0', '1200', '1800', '600') ; time
            index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange

        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        Return
        ------

        '''
        import numpy as np

        print('... disaggregation of precipitation with new method.')

        tmpfile = os.path.join(c.inputdir, 'rr_grib_dummy.grb')

        # initialize new numpy arrays for disaggregated fields
        if maxnum:
            lsp_new_np = np.zeros((maxnum, ni * nj, nt * 3), dtype=np.float64)
            cp_new_np = np.zeros((maxnum, ni * nj, nt * 3), dtype=np.float64)
        else:
            lsp_new_np = np.zeros((1, ni * nj, nt * 3), dtype=np.float64)
            cp_new_np = np.zeros((1, ni * nj, nt * 3), dtype=np.float64)

        # do the disaggregation, but neglect the last value of the
        # original time series. This one corresponds for example to
        # 24 hour, which we don't need. we use 0 - 23 UTC for a day.
        if maxnum:
            for inum in range(maxnum):
                for ix in range(ni*nj):
                    lsp_new_np[inum, ix, :] = disaggregation.IA3(lsp_np[inum, ix, :])[:-1]
                    cp_new_np[inum, ix, :] = disaggregation.IA3(cp_np[inum, ix, :])[:-1]
        else:
            for ix in range(ni*nj):
                lsp_new_np[0, ix, :] = disaggregation.IA3(lsp_np[ix, :])[:-1]
                cp_new_np[0, ix, :] = disaggregation.IA3(cp_np[ix, :])[:-1]

        # write to grib files (full/orig times to flux file and inbetween
        # times with step 1 and 2, respectively)
        print('... write disaggregated precipitation to files.')

        if maxnum:
            # remember the index of the number values
            index_number = index_keys.index('number')
            # empty set to save unique ensemble numbers which were already processed
            ens_numbers = set()
            # index for the ensemble number
            inumb = 0
        else:
            inumb = 0

        # index variable of disaggregated fields
        it = 0

        # "product" genereates each possible combination between the
        # values of the index keys
        for prod in product(*index_vals):
            # e.g. prod = ('20170505', '0', '12')
            #             ( date     ,time, step)
            # or   prod = ('0'   , '20170505', '0', '12')
            #             (number, date      ,time, step)

            cdate = prod[index_keys.index('date')]
            ctime = '{:0>2}'.format(int(prod[index_keys.index('time')])//100)
            cstep = '{:0>3}'.format(int(prod[index_keys.index('step')]))

            date = datetime.strptime(cdate + ctime, '%Y%m%d%H')
            date += timedelta(hours=int(cstep))

            start_period, end_period = generate_retrieval_period_boundary(c)
            # skip all temporary times
            # which are outside the retrieval period
            if date < start_period or \
               date > end_period:
                continue

            # the whole process has to be done for each seperate ensemble member
            # therefore, for each new ensemble member we delete old flux values
            # and start collecting flux data from the beginning time step
            if maxnum and prod[index_number] not in ens_numbers:
                ens_numbers.add(prod[index_number])
                inumb = int(prod[index_number])
                it = 0

            # if necessary, add ensemble member number to filename suffix
            # otherwise, add empty string
            if maxnum:
                numbersuffix = '.N{:0>3}'.format(int(prod[index_number]))
            else:
                numbersuffix = ''

            # per original time stamp: write original time step and
            # the two newly generated sub time steps
            if c.purefc:
                fluxfilename = 'flux' + date.strftime('%Y%m%d.%H') + '.' + cstep
            else:
                fluxfilename = 'flux' + date.strftime('%Y%m%d%H') + numbersuffix

            # write original time step to flux file as usual
            fluxfile = GribUtil(os.path.join(c.inputdir, fluxfilename))
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[142],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, 0, lsp_new_np[inumb, :, it]]
                             )
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[143],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, 0, cp_new_np[inumb, :, it]]
                             )

            # rr for first subgrid point is identified by step = 1
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[142],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, '1', lsp_new_np[inumb, :, it+1]]
                             )
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[143],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, '1', cp_new_np[inumb, :, it+1]]
                             )

            # rr for second subgrid point is identified by step = 2
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[142],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, '2', lsp_new_np[inumb, :, it+2]]
                             )
            fluxfile.set_keys(tmpfile, filemode='ab',
                              wherekeynames=['paramId'], wherekeyvalues=[143],
                              keynames=['perturbationNumber', 'date', 'time',
                                        'stepRange', 'values'],
                              keyvalues=[inumb, int(date.strftime('%Y%m%d')),
                                         date.hour*100, '2', cp_new_np[inumb, :, it+2]]
                             )

            it = it + 3 # jump to next original time step in rr fields
        return

    def _create_rr_grib_dummy(self, ifile, inputdir):
        '''Creates a grib file with a dummy message for the two precipitation
        types lsp and cp each.

        Parameters
        ----------
        ifile : str
            Filename of the input file to read the grib messages from.

        inputdir : str, optional
            Path to the directory where the retrieved data is stored.

        Return
        ------

        '''

        gribfile = GribUtil(os.path.join(inputdir, 'rr_grib_dummy.grb'))
        
        gribfile.copy_dummy_msg(ifile, keynames=['paramId','paramId'],
                                keyvalues=[142,143], filemode='wb')        

        return

    def create(self, inputfiles, c):
        '''An index file will be created which depends on the combination
        of "date", "time" and "stepRange" values. This is used to iterate
        over all messages in each grib file which were passed through the
        parameter "inputfiles" to seperate specific parameters into fort.*
        files. Afterwards the FORTRAN program is called to convert
        the data fields all to the same grid and put them in one file
        per unique time step (combination of "date", "time" and
        "stepRange").

        Note
        ----
        This method is based on the ECMWF example index.py
        https://software.ecmwf.int/wiki/display/GRIB/index.py

        Parameters
        ----------
        inputfiles : UioFiles
            Contains a list of files.

        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        Return
        ------

        '''
        from eccodes import (codes_index_select, codes_get,
                             codes_get_values, codes_set_values, codes_set,
                             codes_write, codes_release, codes_new_from_index,
                             codes_index_release)

        # generate start and end timestamp of the retrieval period
        start_period = datetime.strptime(c.start_date + c.time[0], '%Y%m%d%H')
        start_period = start_period + timedelta(hours=int(c.step[0]))
        end_period = datetime.strptime(c.end_date + c.time[-1], '%Y%m%d%H')
        end_period = end_period + timedelta(hours=int(c.step[-1]))

        # @WRF
        # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
        #
        # UNDER CONSTRUCTION !!!
        #
        #if c.wrf:
        #    table128 = init128(_config.PATH_GRIBTABLE)
        #    wrfpars = to_param_id('sp/mslp/skt/2t/10u/10v/2d/z/lsm/sst/ci/sd/\
        #                           stl1/stl2/stl3/stl4/swvl1/swvl2/swvl3/swvl4',
        #                          table128)

        # these numbers are indices for the temporary files "fort.xx"
        # which are used to seperate the grib fields to,
        # for the Fortran program input
        # 10: U,V | 11: T | 12: lnsp | 13: D | 16: sfc fields
        # 17: Q | 18: Q, SL, GG| 19: omega | 21: etadot | 22: clwc+ciwc
        fdict = {'10':None, '11':None, '12':None, '13':None, '16':None,
                 '17':None, '18':None, '19':None, '21':None, '22':None}

        iid = None
        index_vals = None

        # get the values of the keys which are used for distinct access
        # of grib messages via product
        if '/' in self.number:
            # more than one ensemble member is selected
            index_keys = ["number", "date", "time", "step"]
        else:
            index_keys = ["date", "time", "step"]
        iid, index_vals = self._mk_index_values(c.inputdir,
                                                inputfiles,
                                                index_keys)
        # index_vals looks like e.g.:
        # index_vals[0]: ('20171106', '20171107', '20171108') ; date
        # index_vals[1]: ('0', '600', '1200', '1800') ; time
        # index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange

        # "product" genereates each possible combination between the
        # values of the index keys
        for prod in product(*index_vals):
            # e.g. prod = ('20170505', '0', '12')
            #             (  date    ,time, step)

            print('current product: ', prod)

            for i in range(len(index_keys)):
                codes_index_select(iid, index_keys[i], prod[i])

            # get first id from current product
            gid = codes_new_from_index(iid)

            # if there is no data for this specific time combination / product
            # skip the rest of the for loop and start with next timestep/product
            if not gid:
                continue
#============================================================================================
            # remove old fort.* files and open new ones
            # they are just valid for a single product
            for k, f in fdict.items():
                fortfile = os.path.join(c.inputdir, 'fort.' + k)
                silent_remove(fortfile)
                fdict[k] = open(fortfile, 'wb')
#============================================================================================
            # create correct timestamp from the three time informations
            cdate = str(codes_get(gid, 'date'))
            ctime = '{:0>2}'.format(codes_get(gid, 'time') // 100)
            cstep = '{:0>3}'.format(codes_get(gid, 'step'))
            timestamp = datetime.strptime(cdate + ctime, '%Y%m%d%H')
            timestamp += timedelta(hours=int(cstep))
            cdate_hour = datetime.strftime(timestamp, '%Y%m%d%H')

            # if basetime is used, adapt start/end date period
            if c.basetime is not None:
                time_delta = timedelta(hours=12-int(c.dtime))
                start_period = datetime.strptime(c.end_date + str(c.basetime),
                                               '%Y%m%d%H') - time_delta
                end_period = datetime.strptime(c.end_date + str(c.basetime),
                                             '%Y%m%d%H')

            # skip all temporary times
            # which are outside the retrieval period
            if timestamp < start_period or \
               timestamp > end_period:
                continue


            # @WRF
            # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
            #
            # UNDER CONSTRUCTION !!!
            #
            #if c.wrf:
            #    if 'olddate' not in locals() or cdate != olddate:
            #        fwrf = open(os.path.join(c.outputdir,
            #                    'WRF' + cdate + '.' + ctime + '.000.grb2'), 'wb')
            #        olddate = cdate[:]
#============================================================================================
            # savedfields remembers which fields were already used.
            savedfields = []
            # sum of cloud liquid and ice water content
            scwc = None
            while 1:
                if not gid:
                    break
                paramId = codes_get(gid, 'paramId')
                gridtype = codes_get(gid, 'gridType')
                if paramId == 77: # ETADOT
                    codes_write(gid, fdict['21'])
                elif paramId == 130: # T
                    codes_write(gid, fdict['11'])
                elif paramId == 131 or paramId == 132: # U, V wind component
                    codes_write(gid, fdict['10'])
                elif paramId == 133 and gridtype != 'reduced_gg': # Q
                    codes_write(gid, fdict['17'])
                elif paramId == 133 and gridtype == 'reduced_gg': # Q, gaussian
                    codes_write(gid, fdict['18'])
                elif paramId == 135: # W
                    codes_write(gid, fdict['19'])
                elif paramId == 152: # LNSP
                    codes_write(gid, fdict['12'])
                elif paramId == 155 and gridtype == 'sh': # D
                    codes_write(gid, fdict['13'])
                elif paramId == 246 or paramId == 247: # CLWC, CIWC
                    # sum cloud liquid water and ice
                    if scwc is None:
                        scwc = codes_get_values(gid)
                    else:
                        scwc += codes_get_values(gid)
                        codes_set_values(gid, scwc)
                        codes_set(gid, 'paramId', 201031)
                        codes_write(gid, fdict['22'])
                        scwc = None
                # @WRF
                # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
                #
                # UNDER CONSTRUCTION !!!
                #
                #elif c.wrf and paramId in [129, 138, 155] and \
                #      levtype == 'hybrid': # Z, VO, D
                #    # do not do anything right now
                #    # these are specific parameter for WRF
                #    pass
                else:
                    if paramId not in savedfields:
                        # SD/MSL/TCC/10U/10V/2T/2D/Z/LSM/SDOR/CVL/CVH/SR
                        # and all ADDPAR parameter
                        codes_write(gid, fdict['16'])
                        savedfields.append(paramId)
                    else:
                        print('duplicate ' + str(paramId) + ' not written')
                # @WRF
                # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
                #
                # UNDER CONSTRUCTION !!!
                #
                #try:
                #    if c.wrf:
                #        # model layer
                #        if levtype == 'hybrid' and \
                #           paramId in [129, 130, 131, 132, 133, 138, 155]:
                #            codes_write(gid, fwrf)
                #        # sfc layer
                #        elif paramId in wrfpars:
                #            codes_write(gid, fwrf)
                #except AttributeError:
                #    pass

                codes_release(gid)
                gid = codes_new_from_index(iid)
#============================================================================================
            for f in fdict.values():
                f.close()
#============================================================================================
            # call for Fortran program to convert e.g. reduced_gg grids to
            # regular_ll and calculate detadot/dp
            pwd = os.getcwd()
            os.chdir(c.inputdir)
            if os.stat('fort.21').st_size == 0 and c.eta:
                print('Parameter 77 (etadot) is missing, most likely it is '
                      'not available for this type or date / time\n')
                print('Check parameters CLASS, TYPE, STREAM, START_DATE\n')
                my_error('fort.21 is empty while parameter eta '
                         'is set to 1 in CONTROL file')
# ============================================================================================
            # write out all output to log file before starting fortran programm
            sys.stdout.flush()

            # Fortran program creates file fort.15 (with u,v,etadot,t,sp,q)
            execute_subprocess([os.path.join(c.exedir,
                                             _config.FORTRAN_EXECUTABLE)],
                               error_msg='FORTRAN PROGRAM FAILED!')#shell=True)

            os.chdir(pwd)
# ============================================================================================
            # create name of final output file, e.g. EN13040500 (ENYYMMDDHH)
            # for CERA-20C we need all 4 digits for the year sinc 1900 - 2010
            if c.purefc:
                if c.marsclass == 'EP':
                    suffix = cdate[0:8] + '.' + ctime + '.' + cstep
                else:
                    suffix = cdate[2:8] + '.' + ctime + '.' + cstep
            else:
                if c.marsclass == 'EP':
                    suffix = cdate_hour[0:10]
                else:
                    suffix = cdate_hour[2:10]

            # if necessary, add ensemble member number to filename suffix
            if 'number' in index_keys:
                index_number = index_keys.index('number')
                if len(index_vals[index_number]) > 1:
                    suffix = suffix + '.N{:0>3}'.format(int(prod[index_number]))

            fnout = os.path.join(c.inputdir, c.prefix + suffix)
            print("outputfile = " + fnout)
            # collect for final processing
            self.outputfilelist.append(os.path.basename(fnout))
            # # get additional precipitation subgrid data if available
            # if c.rrint:
                # self.outputfilelist.append(os.path.basename(fnout + '_1'))
                # self.outputfilelist.append(os.path.basename(fnout + '_2'))
# ============================================================================================
            # create outputfile and copy all data from intermediate files
            # to the outputfile (final GRIB input files for FLEXPART)
            orolsm = os.path.basename(glob.glob(c.inputdir +
                                                '/OG_OROLSM__SL.*.' +
                                                c.ppid +
                                                '*')[0])
            if c.marsclass == 'EP':
                fluxfile = 'flux' + suffix
            else:
                fluxfile = 'flux' + cdate[0:2] + suffix
            if not c.cwc:
                flist = ['fort.15', fluxfile, 'fort.16', orolsm]
            else:
                flist = ['fort.15', 'fort.22', fluxfile, 'fort.16', orolsm]

            with open(fnout, 'wb') as fout:
                for f in flist:
                    shutil.copyfileobj(open(os.path.join(c.inputdir, f), 'rb'),
                                       fout)

            if c.omega:
                with open(os.path.join(c.outputdir, 'OMEGA'), 'wb') as fout:
                    shutil.copyfileobj(open(os.path.join(c.inputdir, 'fort.25'),
                                            'rb'), fout)
# ============================================================================================

        # @WRF
        # THIS IS NOT YET CORRECTLY IMPLEMENTED !!!
        #
        # UNDER CONSTRUCTION !!!
        #
        #if c.wrf:
        #    fwrf.close()

        codes_index_release(iid)

        return


    def calc_extra_elda(self, path, prefix):
        ''' Calculates extra ensemble members for ELDA - Stream.

        This is a specific feature which doubles the number of ensemble members
        for the ELDA Stream.

        Parameters
        ----------
        path : str
            Path to the output files.

        prefix : str
            The prefix of the output filenames as defined in Control file.

        Return
        ------

        '''
        from eccodes import (codes_grib_new_from_file, codes_get_array,
                             codes_set_array, codes_release,
                             codes_set, codes_write)

        # max number
        maxnum = int(self.number.split('/')[-1])

        # get a list of all prepared output files with control forecast (CF)
        cf_filelist = UioFiles(path, prefix + '*.N000')
        cf_filelist.files = sorted(cf_filelist.files)

        for cffile in cf_filelist.files:
            with open(cffile, 'rb') as f:
                cfvalues = []
                while True:
                    fid = codes_grib_new_from_file(f)
                    if fid is None:
                        break
                    cfvalues.append(codes_get_array(fid, 'values'))
                    codes_release(fid)

            filename = cffile.split('N000')[0]
            for i in range(1, maxnum + 1):
                # read an ensemble member
                g = open(filename + 'N{:0>3}'.format(i), 'rb')
                # create file for newly calculated ensemble member
                h = open(filename + 'N{:0>3}'.format(i+maxnum), 'wb')
                # number of message in grib file
                j = 0
                while True:
                    gid = codes_grib_new_from_file(g)
                    if gid is None:
                        break
                    values = codes_get_array(gid, 'values')
                    # generate a new ensemble member by subtracting
                    # 2 * ( current time step value - last time step value )
                    codes_set_array(gid, 'values',
                                    values-2*(values-cfvalues[j]))
                    codes_set(gid, 'number', i+maxnum)
                    codes_write(gid, h)
                    codes_release(gid)
                    j += 1

                g.close()
                h.close()
                print('wrote ' + filename + 'N{:0>3}'.format(i+maxnum))
                self.outputfilelist.append(
                    os.path.basename(filename + 'N{:0>3}'.format(i+maxnum)))

        return


    def process_output(self, c):
        '''Postprocessing of FLEXPART input files.

        The grib files are postprocessed depending on the selection in
        CONTROL file. The resulting files are moved to the output
        directory if its not equal to the input directory.
        The following modifications might be done if
        properly switched in CONTROL file:
        GRIB2 - Conversion to GRIB2
        ECTRANS - Transfer of files to gateway server
        ECSTORAGE - Storage at ECMWF server

        Parameters
        ----------
        c : ControlFile
            Contains all the parameters of CONTROL file and
            command line.

        Return
        ------

        '''

        print('\n\nPostprocessing:\n Format: {}\n'.format(c.format))

        if _config.FLAG_ON_ECMWFSERVER:
            print('ecstorage: {}\n ecfsdir: {}\n'.
                  format(c.ecstorage, c.ecfsdir))
            print('ectrans: {}\n gateway: {}\n destination: {}\n '
                  .format(c.ectrans, c.gateway, c.destination))

        print('Output filelist: ')
        print(sorted(self.outputfilelist))

        for ofile in self.outputfilelist:
            ofile = os.path.join(self.inputdir, ofile)

            if c.format.lower() == 'grib2':
                execute_subprocess(['grib_set', '-s', 'edition=2,' +
                                    'productDefinitionTemplateNumber=8',
                                    ofile, ofile + '_2'],
                                   error_msg='GRIB2 CONVERSION FAILED!')

                execute_subprocess(['mv', ofile + '_2', ofile],
                                   error_msg='RENAMING FOR NEW GRIB2 FORMAT '
                                   'FILES FAILED!')

            if c.ectrans and _config.FLAG_ON_ECMWFSERVER:
                execute_subprocess(['ectrans', '-overwrite', '-gateway',
                                    c.gateway, '-remote', c.destination,
                                    '-source', ofile],
                                   error_msg='TRANSFER TO LOCAL SERVER FAILED!')

            if c.ecstorage and _config.FLAG_ON_ECMWFSERVER:
                execute_subprocess(['ecp', '-o', ofile,
                                    os.path.expandvars(c.ecfsdir)],
                                   error_msg='COPY OF FILES TO ECSTORAGE '
                                   'AREA FAILED!')

            if c.outputdir != c.inputdir:
                execute_subprocess(['mv', os.path.join(c.inputdir, ofile),
                                    c.outputdir],
                                   error_msg='RELOCATION OF OUTPUT FILES '
                                   'TO OUTPUTDIR FAILED!')

        return
