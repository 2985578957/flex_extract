#!/usr/bin/env python
# -*- coding: utf-8 -*-
#************************************************************************
# TODO AP
#AP
# - specifiy file header documentation
# - apply classtests
# - add references to ECMWF specific software packages
#************************************************************************
"""
@Author: Anne Fouilloux (University of Oslo)

@Date: October 2014

@ChangeHistory:
    November 2015 - Leopold Haimberger (University of Vienna):
        - extended with Class Control
        - removed functions mkdir_p, daterange, years_between, months_between
        - added functions darain, dapoly, toparamId, init128, normalexit,
          myerror, cleanup, install_args_and_control,
          interpret_args_and_control,
        - removed function __del__ in class EIFLexpart
        - added the following functions in EIFlexpart:
            - create_namelist
            - process_output
            - deacc_fluxes
        - modified existing EIFlexpart - functions for the use in
          flex_extract
        - retrieve also longer term forecasts, not only analyses and
          short term forecast data
        - added conversion into GRIB2
        - added conversion into .fp format for faster execution of FLEXPART
          (see https://www.flexpart.eu/wiki/FpCtbtoWo4FpFormat)

    February 2018 - Anne Philipp (University of Vienna):
        - applied PEP8 style guide
        - added documentation
        - outsourced class Control
        - outsourced class MarsRetrieval
        - changed class name from EIFlexpart to ECFlexpart
        - applied minor code changes (style)

@License:
    (C) Copyright 2014-2018.

    This software is licensed under the terms of the Apache Licence Version 2.0
    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

@Requirements:
    - A standard python 2.6 or 2.7 installation
    - dateutils
    - matplotlib (optional, for debugging)
    - ECMWF specific packages, all available from https://software.ecmwf.int/
        ECMWF WebMARS, gribAPI with python enabled, emoslib and
        ecaccess web toolkit

@Description:
    Further documentation may be obtained from www.flexpart.eu.

    Functionality provided:
        Prepare input 3D-wind fields in hybrid coordinates +
        surface fields for FLEXPART runs
"""
# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------
import subprocess
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import traceback
import shutil
import os
import errno
import sys
import inspect
import glob
import datetime
from string import atoi
from numpy import *
ecapi = True
try:
    import ecmwfapi
except ImportError:
    ecapi = False
from gribapi import *
from GribTools import GribTools
from Tools import init128, toparamId, silentremove, product
from Control import Control
from MARSretrieval import MARSretrieval
import Disagg
# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class ECFlexpart:
    '''
    Class to retrieve ECMWF data specific for running FLEXPART.
    '''
    # --------------------------------------------------------------------------
    # CLASS FUNCTIONS
    # --------------------------------------------------------------------------
    def __init__(self, c, fluxes=False): #done/ verstehen
        '''
        @Description:
            Creates an object/instance of ECFlexpart with the
            associated settings of its attributes for the retrieval.

        @Input:
            self: instance of ECFlexpart
                The current object of the class.

            c: instance of class Control
                Contains all the parameters of control files, which are e.g.:
                DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
                STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
                LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
                OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
                ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
                MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
                DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

                For more information about format and content of the parameter
                see documentation.

            fluxes: boolean, optional
                Decides if a the flux parameter settings are stored or
                the rest of the parameter list.
                Default value is False.

        @Return:
            <nothing>
        '''

        # different mars types for retrieving reanalysis data for flexpart
        self.types = dict()
        try:
            if c.maxstep > len(c.type):    # Pure forecast mode
                c.type = [c.type[1]]
                c.step = ['{:0>3}'.format(int(c.step[0]))]
                c.time = [c.time[0]]
                for i in range(1, c.maxstep + 1):
                    c.type.append(c.type[0])
                    c.step.append('{:0>3}'.format(i))
                    c.time.append(c.time[0])
        except:
            pass

        self.inputdir = c.inputdir
        self.basetime = c.basetime
        self.dtime = c.dtime
        #self.mars = {}
        i = 0
        #j = 0
        if fluxes is True and c.maxstep < 24:
            # no forecast beyond one day is needed!
            # Thus, prepare flux data manually as usual
            # with only FC fields with start times at 00/12
            # (but without 00/12 fields since these are
            # the initialisation times of the flux fields
            # and therefore are zero all the time)
            self.types['FC'] = {'times': '00/12',
                                'steps': '{}/to/12/by/{}'.format(c.dtime,
                                                                      c.dtime)}
            #i = 1
            #for k in [0, 12]:
            #    for j in range(int(c.dtime), 13, int(c.dtime)):
            #        self.mars['{:0>3}'.format(i * int(c.dtime))] = \
            #               [c.type[1], '{:0>2}'.format(k), '{:0>3}'.format(j)]
            #        i += 1
        else:
            for ty, st, ti in zip(c.type, c.step, c.time):
                btlist = range(24)
                if c.basetime == '12':
                    btlist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
                if c.basetime == '00':
                    btlist = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0]

                if mod(i, int(c.dtime)) == 0 and \
                    (c.maxstep > 24 or i in btlist):

                    if ty not in self.types.keys():
                        self.types[ty] = {'times': '', 'steps': ''}

                    if ti not in self.types[ty]['times']:
                        if len(self.types[ty]['times']) > 0:
                            self.types[ty]['times'] += '/'
                        self.types[ty]['times'] += ti

                    if st not in self.types[ty]['steps']:
                        if len(self.types[ty]['steps']) > 0:
                            self.types[ty]['steps'] += '/'
                        self.types[ty]['steps'] += st

                    #self.mars['{:0>3}'.format(j)] = [ty,
                    #                                 '{:0>2}'.format(int(ti)),
                    #                                 '{:0>3}'.format(int(st))]
                    #j += int(c.dtime)

                i += 1
            print 'EC init: ', self.types #AP
        # Different grids need different retrievals
        # SH = Spherical Harmonics, GG = Gaussian Grid,
        # OG = Output Grid, ML = MultiLevel, SL = SingleLevel
        self.params = {'SH__ML': '', 'SH__SL': '',
                       'GG__ML': '', 'GG__SL': '',
                       'OG__ML': '', 'OG__SL': '',
                       'OG_OROLSM_SL': '', 'OG_acc_SL': ''}
        self.marsclass = c.marsclass
        self.stream = c.stream
        self.number = c.number
        self.resol = c.resol
        self.accuracy = c.accuracy
        self.level = c.level
        try:
            self.levelist = c.levelist
        except:
            self.levelist = '1/to/' + c.level

        # for gaussian grid retrieval
        self.glevelist = '1/to/' + c.level

        try:
            self.gaussian = c.gaussian
        except:
            self.gaussian = ''

        try:
            self.expver = c.expver
        except:
            self.expver = '1'

        try:
            self.number = c.number
        except:
            self.number = '0'

        if 'N' in c.grid:  # Gaussian output grid
            self.grid = c.grid
            self.area = 'G'
        else:
            self.grid = '{}/{}'.format(int(c.grid) / 1000., int(c.grid) / 1000.)
            self.area = '{}/{}/{}/{}'.format(int(c.upper) / 1000.,
                                             int(c.left) / 1000.,
                                             int(c.lower) / 1000.,
                                             int(c.right) / 1000.)

        self.outputfilelist = []


        # Now comes the nasty part that deals with the different
        # scenarios we have:
        # 1) Calculation of etadot on
        #    a) Gaussian grid
        #    b) Output grid
        #    c) Output grid using parameter 77 retrieved from MARS
        # 3) Calculation/Retrieval of omega
        # 4) Download also data for WRF

        if fluxes is False:
            self.params['SH__SL'] = ['LNSP', 'ML', '1', 'OFF']
            #                        "SD/MSL/TCC/10U/10V/2T/2D/129/172"
            self.params['OG__SL'] = ["141/151/164/165/166/167/168/129/172", \
                                     'SFC', '1', self.grid]
            if len(c.addpar) > 0:
                if c.addpar[0] == '/':
                    c.addpar = c.addpar[1:]
                self.params['OG__SL'][0] += '/' + '/'.join(c.addpar)

            self.params['OG_OROLSM__SL'] = ["160/27/28/173", \
                                            'SFC', '1', self.grid]

            self.params['OG__ML'] = ['T/Q', 'ML', self.levelist, self.grid]

            if c.gauss == '0' and c.eta == '1':
                # the simplest case
                self.params['OG__ML'][0] += '/U/V/77'
            elif c.gauss == '0' and c.eta == '0':
#AP then remove?!?!?!?       # this is not recommended (inaccurate)
                self.params['OG__ML'][0] += '/U/V'
            elif c.gauss == '1' and c.eta == '0':
                # this is needed for data before 2008, or for reanalysis data
                self.params['GG__SL'] = ['Q', 'ML', '1', \
                                         '{}'.format((int(self.resol) + 1) / 2)]
                self.params['SH__ML'] = ['U/V/D', 'ML', self.glevelist, 'OFF']
            else:
                print('Warning: This is a very costly parameter combination, \
                       use only for debugging!')
                self.params['GG__SL'] = ['Q', 'ML', '1', \
                                         '{}'.format((int(self.resol) + 1) / 2)]
                self.params['GG__ML'] = ['U/V/D/77', 'ML', self.glevelist, \
                                         '{}'.format((int(self.resol) + 1) / 2)]

            if c.omega == '1':
                self.params['OG__ML'][0] += '/W'

            try:
                # add cloud water content if necessary
                if c.cwc == '1':
                    self.params['OG__ML'][0] += '/CLWC/CIWC'
            except:
                pass

            try:
                # add vorticity and geopotential height for WRF if necessary
                if c.wrf == '1':
                    self.params['OG__ML'][0] += '/Z/VO'
                    if '/D' not in self.params['OG__ML'][0]:
                        self.params['OG__ML'][0] += '/D'
                    #wrf_sfc = 'sp/msl/skt/2t/10u/10v/2d/z/lsm/sst/ci/sd/stl1/ /
                    #           stl2/stl3/stl4/swvl1/swvl2/swvl3/swvl4'.upper()
                    wrf_sfc = '134/235/167/165/166/168/129/172/34/31/141/ \
                               139/170/183/236/39/40/41/42'.upper()
                    lwrt_sfc = wrf_sfc.split('/')
                    for par in lwrt_sfc:
                        if par not in self.params['OG__SL'][0]:
                            self.params['OG__SL'][0] += '/' + par
            except:
                pass
        else:
            self.params['OG_acc_SL'] = ["LSP/CP/SSHF/EWSS/NSSS/SSR", \
                                        'SFC', '1', self.grid]

        # if needed, add additional WRF specific parameters here

        return


    def write_namelist(self, c, filename): #done
        '''
        @Description:
            Creates a namelist file in the temporary directory and writes
            the following values to it: maxl, maxb, mlevel,
            mlevelist, mnauf, metapar, rlo0, rlo1, rla0, rla1,
            momega, momegadiff, mgauss, msmooth, meta, metadiff, mdpdeta

        @Input:
            self: instance of ECFlexpart
                The current object of the class.

            c: instance of class Control
                Contains all the parameters of control files, which are e.g.:
                DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
                STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
                LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
                OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
                ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
                MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
                DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

                For more information about format and content of the parameter
                see documentation.

            filename: string
                Name of the namelist file.

        @Return:
            <nothing>
        '''

        self.inputdir = c.inputdir
        area = asarray(self.area.split('/')).astype(float)
        grid = asarray(self.grid.split('/')).astype(float)

        if area[1] > area[3]:
            area[1] -= 360
        zyk = abs((area[3] - area[1] - 360.) + grid[1]) < 1.e-6
        maxl = int((area[3] - area[1]) / grid[1]) + 1
        maxb = int((area[0] - area[2]) / grid[0]) + 1

        with open(self.inputdir + '/' + filename, 'w') as f:
            f.write('&NAMGEN\n')
            f.write(',\n  '.join(['maxl = ' + str(maxl), 'maxb = ' + str(maxb),
                    'mlevel = ' + self.level,
                    'mlevelist = ' + '"' + self.levelist + '"',
                    'mnauf = ' + self.resol, 'metapar = ' + '77',
                    'rlo0 = ' + str(area[1]), 'rlo1 = ' + str(area[3]),
                    'rla0 = ' + str(area[2]), 'rla1 = ' + str(area[0]),
                    'momega = ' + c.omega, 'momegadiff = ' + c.omegadiff,
                    'mgauss = ' + c.gauss, 'msmooth = ' + c.smooth,
                    'meta = ' + c.eta, 'metadiff = ' + c.etadiff,
                    'mdpdeta = ' + c.dpdeta]))

            f.write('\n/\n')

        return

    def retrieve(self, server, dates, times, inputdir=''):
        '''
        @Description:


        @Input:
            self: instance of ECFlexpart

            server: instance of ECMWFService

            dates:

            times:

            inputdir: string, optional
                Default string is empty ('').

        @Return:
            <nothing>
        '''
        self.dates = dates
        self.server = server

        if inputdir == "":
            self.inputdir = '.'
        else:
            self.inputdir = inputdir

        # Retrieve Q not for using Q but as a template for a reduced gaussian
        # grid one date and time is enough
        # Take analysis at 00
        qdate = self.dates
        idx = qdate.find("/")
        if (idx > 0):
            qdate = self.dates[:idx]

        #QG =  MARSretrieval(self.server, marsclass = self.marsclass, stream = self.stream, type = "an", levtype = "ML", levelist = "1",
                             #gaussian = "reduced",grid = '{}'.format((int(self.resol)+1)/2), resol = self.resol,accuracy = self.accuracy,target = self.inputdir+"/"+"QG.grb",
                             #date = qdate, time = "00",expver = self.expver, param = "133.128")
        #QG.displayInfo()
        #QG.dataRetrieve()

        oro = False
        for ftype in self.types:
            for pk, pv in self.params.iteritems():
                if isinstance(pv, str):
                    continue
                mftype = '' + ftype
                mftime = self.types[ftype]['times']
                mfstep = self.types[ftype]['steps']
                mfdate = self.dates
                mfstream = self.stream
                mftarget = self.inputdir + "/" + ftype + pk + '.' + \
                           self.dates.split('/')[0] + '.' + str(os.getppid()) +\
                           '.' + str(os.getpid()) + ".grb"
                if pk == 'OG__SL':
                    pass
                if pk == 'OG_OROLSM__SL':
                    if oro is False:
                        mfstream = 'OPER'
                        mftype = 'AN'
                        mftime = '00'
                        mfstep = '000'
                        mfdate = self.dates.split('/')[0]
                        mftarget = self.inputdir + "/" + pk + '.' + mfdate + \
                                   '.' + str(os.getppid()) + '.' + \
                                   str(os.getpid()) + ".grb"
                        oro = True
                    else:
                        continue

                if pk == 'GG__SL' and pv[0] == 'Q':
                    area = ""
                    gaussian = 'reduced'
                else:
                    area = self.area
                    gaussian = self.gaussian

                if self.basetime is None:
                    MR = MARSretrieval(self.server,
                            marsclass=self.marsclass, stream=mfstream,
                            type=mftype, levtype=pv[1], levelist=pv[2],
                            resol=self.resol, gaussian=gaussian,
                            accuracy=self.accuracy, grid=pv[3],
                            target=mftarget, area=area, date=mfdate,
                            time=mftime, number=self.number, step=mfstep,
                            expver=self.expver, param=pv[0])

                    MR.displayInfo()
                    MR.dataRetrieve()
    # The whole else section is only necessary for operational scripts.
    # It could be removed
                else:
                    # check if mars job requests fields beyond basetime.
                    # If yes eliminate those fields since they may not
                    # be accessible with user's credentials
                    sm1 = -1
                    if 'by' in mfstep:
                        sm1 = 2
                    tm1 = -1
                    if 'by' in mftime:
                        tm1 = 2
                    maxtime = datetime.datetime.strptime(
                                mfdate.split('/')[-1] + mftime.split('/')[tm1],
                                '%Y%m%d%H') + datetime.timedelta(
                                hours=int(mfstep.split('/')[sm1]))

                    elimit = datetime.datetime.strptime(
                                mfdate.split('/')[-1] +
                                self.basetime, '%Y%m%d%H')

                    if self.basetime == '12':
                        if 'acc' in pk:

                # Strategy: if maxtime-elimit> = 24h reduce date by 1,
                # if 12h< = maxtime-elimit<12h reduce time for last date
                # if maxtime-elimit<12h reduce step for last time
                # A split of the MARS job into 2 is likely necessary.
                            maxtime = elimit-datetime.timedelta(hours=24)
                            mfdate = '/'.join(('/'.join(mfdate.split('/')[:-1]),
                                                datetime.datetime.strftime(
                                                maxtime, '%Y%m%d')))

                            MR = MARSretrieval(self.server,
                                            marsclass=self.marsclass,
                                            stream=self.stream, type=mftype,
                                            levtype=pv[1], levelist=pv[2],
                                            resol=self.resol, gaussian=gaussian,
                                            accuracy=self.accuracy, grid=pv[3],
                                            target=mftarget, area=area,
                                            date=mfdate, time=mftime,
                                            number=self.number, step=mfstep,
                                            expver=self.expver, param=pv[0])

                            MR.displayInfo()
                            MR.dataRetrieve()

                            maxtime = elimit - datetime.timedelta(hours=12)
                            mfdate = datetime.datetime.strftime(maxtime,
                                                                '%Y%m%d')
                            mftime = '00'
                            mftarget = self.inputdir + "/" + ftype + pk + \
                                       '.' + mfdate + '.' + str(os.getppid()) +\
                                       '.' + str(os.getpid()) + ".grb"

                            MR = MARSretrieval(self.server,
                                            marsclass=self.marsclass,
                                            stream=self.stream, type=mftype,
                                            levtype=pv[1], levelist=pv[2],
                                            resol=self.resol, gaussian=gaussian,
                                            accuracy=self.accuracy, grid=pv[3],
                                            target=mftarget, area=area,
                                            date=mfdate, time=mftime,
                                            number=self.number, step=mfstep,
                                            expver=self.expver, param=pv[0])

                            MR.displayInfo()
                            MR.dataRetrieve()
                        else:
                            MR = MARSretrieval(self.server,
                                            marsclass=self.marsclass,
                                            stream=self.stream, type=mftype,
                                            levtype=pv[1], levelist=pv[2],
                                            resol=self.resol, gaussian=gaussian,
                                            accuracy=self.accuracy, grid=pv[3],
                                            target=mftarget, area=area,
                                            date=mfdate, time=mftime,
                                            number=self.number, step=mfstep,
                                            expver=self.expver, param=pv[0])

                            MR.displayInfo()
                            MR.dataRetrieve()
                    else:
                        maxtime = elimit - datetime.timedelta(hours=24)
                        mfdate = datetime.datetime.strftime(maxtime,'%Y%m%d')

                        mftimesave = ''.join(mftime)

                        if '/' in mftime:
                            times = mftime.split('/')
                            while ((int(times[0]) +
                                   int(mfstep.split('/')[0]) <= 12) and
                                  (pk != 'OG_OROLSM__SL') and 'acc' not in pk):
                                times = times[1:]
                            if len(times) > 1:
                                mftime = '/'.join(times)
                            else:
                                mftime = times[0]

                        MR = MARSretrieval(self.server,
                                        marsclass=self.marsclass,
                                        stream=self.stream, type=mftype,
                                        levtype=pv[1], levelist=pv[2],
                                        resol=self.resol, gaussian=gaussian,
                                        accuracy=self.accuracy, grid=pv[3],
                                        target=mftarget, area=area,
                                        date=mfdate, time=mftime,
                                        number=self.number, step=mfstep,
                                        expver=self.expver, param=pv[0])

                        MR.displayInfo()
                        MR.dataRetrieve()

                        if (int(mftimesave.split('/')[0]) == 0 and
                            int(mfstep.split('/')[0]) == 0 and
                            pk != 'OG_OROLSM__SL'):
                            mfdate = datetime.datetime.strftime(elimit,'%Y%m%d')
                            mftime = '00'
                            mfstep = '000'
                            mftarget = self.inputdir + "/" + ftype + pk + \
                                       '.' + mfdate + '.' + str(os.getppid()) +\
                                       '.' + str(os.getpid()) + ".grb"

                            MR = MARSretrieval(self.server,
                                        marsclass=self.marsclass,
                                        stream=self.stream, type=mftype,
                                        levtype=pv[1], levelist=pv[2],
                                        resol=self.resol, gaussian=gaussian,
                                        accuracy=self.accuracy, grid=pv[3],
                                        target=mftarget, area=area,
                                        date=mfdate, time=mftime,
                                        number=self.number, step=mfstep,
                                        expver=self.expver, param=pv[0])

                            MR.displayInfo()
                            MR.dataRetrieve()

        print("MARS retrieve done... ")

        return


    def process_output(self, c): #done
        '''
        @Description:
            The grib files are postprocessed depending on selection in
            control file. The resulting files are moved to the output
            directory if its not equla to the input directory.
            The following modifications might be done if
            properly switched in control file:
            GRIB2 - Conversion to GRIB2
            ECTRANS - Transfer of files to gateway server
            ECSTORAGE - Storage at ECMWF server
            GRIB2FLEXPART - Conversion of GRIB files to FLEXPART binary format

        @Input:
            self: instance of ECFlexpart
                The current object of the class.

            c: instance of class Control
                Contains all the parameters of control files, which are e.g.:
                DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
                STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
                LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
                OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
                ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
                MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
                DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

                For more information about format and content of the parameter
                see documentation.

        @Return:
            <nothing>

        '''

        print('Postprocessing:\n Format: {}\n'.format(c.format))

        if c.ecapi is False:
            print('ecstorage: {}\n ecfsdir: {}\n'.
                  format(c.ecstorage, c.ecfsdir))
            if not hasattr(c, 'gateway'):
                c.gateway = os.getenv('GATEWAY')
            if not hasattr(c, 'destination'):
                c.destination = os.getenv('DESTINATION')
            print('ectrans: {}\n gateway: {}\n destination: {}\n '
                    .format(c.ectrans, c.gateway, c.destination))

        print('Output filelist: \n')
        print(self.outputfilelist)

        if c.format.lower() == 'grib2':
            for ofile in self.outputfilelist:
                p = subprocess.check_call(['grib_set', '-s', 'edition=2, \
                                            productDefinitionTemplateNumber=8',
                                            ofile, ofile + '_2'])
                p = subprocess.check_call(['mv', ofile + '_2', ofile])

        if int(c.ectrans) == 1 and c.ecapi is False:
            for ofile in self.outputfilelist:
                p = subprocess.check_call(['ectrans', '-overwrite', '-gateway',
                                           c.gateway, '-remote', c.destination,
                                           '-source', ofile])
                print('ectrans:', p)

        if int(c.ecstorage) == 1 and c.ecapi is False:
            for ofile in self.outputfilelist:
                p = subprocess.check_call(['ecp', '-o', ofile,
                                           os.path.expandvars(c.ecfsdir)])

        if c.outputdir != c.inputdir:
            for ofile in self.outputfilelist:
                p = subprocess.check_call(['mv', ofile, c.outputdir])

        # prepare environment for the grib2flexpart run
        # to convert grib to flexpart binary
        if c.grib2flexpart == '1':

            # generate AVAILABLE file
            # Example of AVAILABLE file data
            # 20131107 000000      EN13110700              ON DISC
            clist = []
            for ofile in self.outputfilelist:
                fname = ofile.split('/')
                if '.' in fname[-1]:
                    l = fname[-1].split('.')
                    timestamp = datetime.datetime.strptime(l[0][-6:] + l[1],
                                                           '%y%m%d%H')
                    timestamp += datetime.timedelta(hours=int(l[2]))
                    cdate = datetime.datetime.strftime(timestamp, '%Y%m%d')
                    chms = datetime.datetime.strftime(timestamp, '%H%M%S')
                else:
                    cdate = '20' + fname[-1][-8:-2]
                    chms = fname[-1][-2:] + '0000'
                clist.append(cdate + ' ' + chms + ' '*6 +
                             fname[-1] + ' '*14 + 'ON DISC')
            clist.sort()
            with open(c.outputdir + '/' + 'AVAILABLE', 'w') as f:
                f.write('\n'.join(clist) + '\n')

            # generate pathnames file
            pwd = os.path.abspath(c.outputdir)
            with open(pwd + '/pathnames','w') as f:
                f.write(pwd + '/Options/\n')
                f.write(pwd + '/\n')
                f.write(pwd + '/\n')
                f.write(pwd + '/AVAILABLE\n')
                f.write(' = == = == = == = == = == ==  = \n')

            # create Options dir if necessary
            if not os.path.exists(pwd + '/Options'):
                os.makedirs(pwd+'/Options')

            # read template COMMAND file
            with open(os.path.expandvars(
                     os.path.expanduser(c.flexpart_root_scripts)) +
                     '/../Options/COMMAND', 'r') as f:
                lflist = f.read().split('\n')

            # find index of list where to put in the
            # date and time information
            # usually after the LDIRECT parameter
            i = 0
            for l in lflist:
                if 'LDIRECT' in l.upper():
                    break
                i += 1

#            clist.sort()
            # insert the date and time information of run star and end
            # into the list of lines of COMMAND file
            lflist = lflist[:i+1] + \
                     [clist[0][:16], clist[-1][:16]] + \
                     lflist[i+3:]

            # write the new COMMAND file
            with open(pwd + '/Options/COMMAND', 'w') as g:
                g.write('\n'.join(lflist) + '\n')

            # change to outputdir and start the
            # grib2flexpart run
            # afterwards switch back to the working dir
            os.chdir(c.outputdir)
            p = subprocess.check_call([os.path.expandvars(
                        os.path.expanduser(c.flexpart_root_scripts)) +
                        '/../FLEXPART_PROGRAM/grib2flexpart',
                        'useAvailable', '.'])
            os.chdir(pwd)

        return

    def create(self, inputfiles, c): #done
        '''
        @Description:
            This method is based on the ECMWF example index.py
            https://software.ecmwf.int/wiki/display/GRIB/index.py

            An index file will be created which depends on the combination
            of "date", "time" and "stepRange" values. This is used to iterate
            over all messages in the grib files passed through the parameter
            "inputfiles" to seperate specific parameters into fort.* files.
            Afterwards the FORTRAN program Convert2 is called to convert
            the data fields all to the same grid and put them in one file
            per day.

        @Input:
            self: instance of ECFlexpart
                The current object of the class.

            inputfiles: instance of UIOFiles
                Contains a list of files.

            c: instance of class Control
                Contains all the parameters of control files, which are e.g.:
                DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
                STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
                LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
                OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
                ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
                MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
                DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

                For more information about format and content of the parameter
                see documentation.

        @Return:
            <nothing>
        '''

        table128 = init128(c.ecmwfdatadir +
                           '/grib_templates/ecmwf_grib1_table_128')
        wrfpars = toparamId('sp/mslp/skt/2t/10u/10v/2d/z/lsm/sst/ci/sd/\
                            stl1/stl2/stl3/stl4/swvl1/swvl2/swvl3/swvl4',
                            table128)

        index_keys = ["date", "time", "step"]
        indexfile = c.inputdir + "/date_time_stepRange.idx"
        silentremove(indexfile)
        grib = GribTools(inputfiles.files)
        # creates new index file
        iid = grib.index(index_keys=index_keys, index_file=indexfile)

        # read values of index keys
        index_vals = []
        for key in index_keys:
            index_vals.append(grib_index_get(iid, key))
            print(index_vals[-1])
            # index_vals looks for example like:
            # index_vals[0]: ('20171106', '20171107', '20171108') ; date
            # index_vals[1]: ('0', '1200', '1800', '600') ; time
            # index_vals[2]: ('0', '12', '3', '6', '9') ; stepRange

        # delete old fort.* files and open them newly
        fdict = {'10':None, '11':None, '12':None, '13':None, '16':None,
                 '17':None, '19':None, '21':None, '22':None, '20':None}
        #for f in fdict.keys():
        #    silentremove(c.inputdir + "/fort." + f)


        for prod in product(*index_vals):
            print 'current prod: ', prod
            # e.g. prod = ('20170505', '0', '12')
            #             (  date    ,time, step)
            # per date e.g. time = 0, 600, 1200, 1800
            # per time e.g. step = 0, 3, 6, 9, 12
            for i in range(len(index_keys)):
                grib_index_select(iid, index_keys[i], prod[i])

            gid = grib_new_from_index(iid)
            # do convert2 program if gid at this time is not None,
            # therefore save in hid
            hid = gid
            if gid is not None:
                for k, f in fdict.iteritems():
                    silentremove(c.inputdir + "/fort." + k)
                    fdict[k] = open(c.inputdir + '/fort.' + k, 'w')

                cdate = str(grib_get(gid, 'date'))
                time = grib_get(gid, 'time')
                type = grib_get(gid, 'type')
                step = grib_get(gid, 'step')
                # create correct timestamp from the three time informations
                # date, time, step
                timestamp = datetime.datetime.strptime(
                                cdate + '{:0>2}'.format(time/100), '%Y%m%d%H')
                timestamp += datetime.timedelta(hours=int(step))

                cdateH = datetime.datetime.strftime(timestamp, '%Y%m%d%H')
                chms = datetime.datetime.strftime(timestamp, '%H%M%S')

                if c.basetime is not None:
                    slimit = datetime.datetime.strptime(
                                c.start_date + '00', '%Y%m%d%H')
                    bt = '23'
                    if c.basetime == '00':
                        bt = '00'
                        slimit = datetime.datetime.strptime(
                                    c.end_date + bt, '%Y%m%d%H') - \
                                    datetime.timedelta(hours=12-int(c.dtime))
                    if c.basetime == '12':
                        bt = '12'
                        slimit = datetime.datetime.strptime(
                                    c.end_date + bt, '%Y%m%d%H') - \
                                 datetime.timedelta(hours=12-int(c.dtime))

                    elimit = datetime.datetime.strptime(
                                c.end_date + bt, '%Y%m%d%H')

                    if timestamp < slimit or timestamp > elimit:
                        continue

            try:
                if c.wrf == '1':
                    if 'olddate' not in locals():
                        fwrf = open(c.outputdir + '/WRF' + cdate +
                                    '.{:0>2}'.format(time) + '.000.grb2', 'w')
                        olddate = cdate[:]
                    else:
                        if cdate != olddate:
                            fwrf = open(c.outputdir + '/WRF' + cdate +
                                        '.{:0>2}'.format(time) + '.000.grb2',
                                        'w')
                            olddate = cdate[:]
            except AttributeError:
                pass


            savedfields = []
            while 1:
                if gid is None:
                    break
                paramId = grib_get(gid, 'paramId')
                gridtype = grib_get(gid, 'gridType')
                datatype = grib_get(gid, 'dataType')
                levtype = grib_get(gid, 'typeOfLevel')
                if paramId == 133 and gridtype == 'reduced_gg':
                # Relative humidity (Q.grb) is used as a template only
                # so we need the first we "meet"
                    with open(c.inputdir + '/fort.18', 'w') as fout:
                        grib_write(gid, fout)
                elif paramId == 131 or paramId == 132:
                    grib_write(gid, fdict['10'])
                elif paramId == 130:
                    grib_write(gid, fdict['11'])
                elif paramId == 133 and gridtype != 'reduced_gg':
                    grib_write(gid, fdict['17'])
                elif paramId == 152:
                    grib_write(gid, fdict['12'])
                elif paramId == 155 and gridtype == 'sh':
                    grib_write(gid, fdict['13'])
                elif paramId in [129, 138, 155] and levtype == 'hybrid' \
                                                and c.wrf == '1':
                    pass
                elif paramId == 246 or paramId == 247:
                    # cloud liquid water and ice
                    if paramId == 246:
                        clwc = grib_get_values(gid)
                    else:
                        clwc += grib_get_values(gid)
                        grib_set_values(gid, clwc)
                        grib_set(gid, 'paramId', 201031)
                        grib_write(gid, fdict['22'])
                elif paramId == 135:
                    grib_write(gid, fdict['19'])
                elif paramId == 77:
                    grib_write(gid, fdict['21'])
                else:
                    if paramId not in savedfields:
                        grib_write(gid, fdict['16'])
                        savedfields.append(paramId)
                    else:
                        print('duplicate ' + str(paramId) + ' not written')

                try:
                    if c.wrf == '1':
# die if abfrage scheint ueberfluessig da eh das gleihce ausgefuehrt wird
                        if levtype == 'hybrid':
                            if paramId in [129, 130, 131, 132, 133, 138, 155]:
                                grib_write(gid, fwrf)
                        else:
                            if paramId in wrfpars:
                                grib_write(gid, fwrf)
                except AttributeError:
                    pass

                grib_release(gid)
                gid = grib_new_from_index(iid)

            for f in fdict.values():
                f.close()

            # call for CONVERT2
# AUSLAGERN IN EIGENE FUNKTION

            if hid is not None:
                pwd = os.getcwd()
                os.chdir(c.inputdir)
                if os.stat('fort.21').st_size == 0 and int(c.eta) == 1:
                    print('Parameter 77 (etadot) is missing, most likely it is \
                           not available for this type or date/time\n')
                    print('Check parameters CLASS, TYPE, STREAM, START_DATE\n')
                    myerror(c, 'fort.21 is empty while parameter eta is set \
                                to 1 in CONTROL file')

                p = subprocess.check_call([os.path.expandvars(
                        os.path.expanduser(c.exedir)) + '/CONVERT2'], shell=True)
                os.chdir(pwd)
                # create the corresponding output file fort.15
                # (generated by CONVERT2)
                # + fort.16 (paramId 167 and paramId 168)
                fnout = c.inputdir + '/' + c.prefix
                if c.maxstep > 12:
                    suffix = cdate[2:8] + '.{:0>2}'.format(time/100) + \
                             '.{:0>3}'.format(step)
                else:
                    suffix = cdateH[2:10]

                fnout += suffix
                print("outputfile = " + fnout)
                self.outputfilelist.append(fnout) # needed for final processing
                fout = open(fnout, 'wb')
                shutil.copyfileobj(open(c.inputdir + '/fort.15', 'rb'), fout)
                if c.cwc == '1':
                    shutil.copyfileobj(open(c.inputdir + '/fort.22', 'rb'), fout)
                shutil.copyfileobj(open(c.inputdir + '/flux' + cdate[0:2] +
                                        suffix, 'rb'), fout)
                shutil.copyfileobj(open(c.inputdir + '/fort.16', 'rb'), fout)
                orolsm = glob.glob(c.inputdir +
                                   '/OG_OROLSM__SL.*.' + c.ppid + '*')[0]
                shutil.copyfileobj(open(orolsm, 'rb'), fout)
                fout.close()
                if c.omega == '1':
                    fnout = c.outputdir + '/OMEGA'
                    fout  =  open(fnout, 'wb')
                    shutil.copyfileobj(open(c.inputdir + '/fort.25', 'rb'), fout)

        try:
            if c.wrf == '1':
                fwrf.close()
        except:
            pass

        grib_index_release(iid)

        return


    def deacc_fluxes(self, inputfiles, c):
        '''
        @Description:


        @Input:
            self: instance of ECFlexpart
                The current object of the class.

            inputfiles: instance of UIOFiles
                Contains a list of files.

            c: instance of class Control
                Contains all the parameters of control files, which are e.g.:
                DAY1(start_date), DAY2(end_date), DTIME, MAXSTEP, TYPE, TIME,
                STEP, CLASS(marsclass), STREAM, NUMBER, EXPVER, GRID, LEFT,
                LOWER, UPPER, RIGHT, LEVEL, LEVELIST, RESOL, GAUSS, ACCURACY,
                OMEGA, OMEGADIFF, ETA, ETADIFF, DPDETA, SMOOTH, FORMAT,
                ADDPAR, WRF, CWC, PREFIX, ECSTORAGE, ECTRANS, ECFSDIR,
                MAILOPS, MAILFAIL, GRIB2FLEXPART, FLEXPARTDIR, BASETIME
                DATE_CHUNK, DEBUG, INPUTDIR, OUTPUTDIR, FLEXPART_ROOT_SCRIPTS

                For more information about format and content of the parameter
                see documentation.

        @Return:
            <nothing>
        '''

        table128 = init128(c.ecmwfdatadir +
                           '/grib_templates/ecmwf_grib1_table_128')
        pars = toparamId(self.params['OG_acc_SL'][0], table128)
        index_keys = ["date", "time", "step"]
        indexfile = c.inputdir + "/date_time_stepRange.idx"
        silentremove(indexfile)
        grib = GribTools(inputfiles.files)
        # creates new index file
        iid = grib.index(index_keys=index_keys, index_file=indexfile)

        # read values of index keys
        index_vals = []
        for key in index_keys:
            key_vals = grib_index_get(iid,key)
            print(key_vals)
            # have to sort the steps for disaggregation,
            # therefore convert to int first
            if key == 'step':
                key_vals = [int(k) for k in key_vals]
                key_vals.sort()
                key_vals = [str(k) for k in key_vals]
            index_vals.append(key_vals)
            # index_vals looks for example like:
            # index_vals[0]: ('20171106', '20171107', '20171108') ; date
            # index_vals[1]: ('0', '1200') ; time
            # index_vals[2]: (3', '6', '9', '12') ; stepRange

        valsdict = {}
        svalsdict = {}
        stepsdict = {}
        for p in pars:
            valsdict[str(p)] = []
            svalsdict[str(p)] = []
            stepsdict[str(p)] = []

        for prod in product(*index_vals):
            # e.g. prod = ('20170505', '0', '12')
            #             (  date    ,time, step)
            # per date e.g. time = 0, 1200
            # per time e.g. step = 3, 6, 9, 12
            for i in range(len(index_keys)):
                grib_index_select(iid, index_keys[i], prod[i])

            gid = grib_new_from_index(iid)
            # do convert2 program if gid at this time is not None,
            # therefore save in hid
            hid = gid
            if gid is not None:
                cdate = grib_get(gid, 'date')
                time = grib_get(gid, 'time')
                type = grib_get(gid, 'type')
                step = grib_get(gid, 'step')
                # date+time+step-2*dtime
                # (since interpolated value valid for step-2*dtime)
                sdate = datetime.datetime(year=cdate/10000,
                                          month=mod(cdate, 10000)/100,
                                          day=mod(cdate, 100),
                                          hour=time/100)
                fdate = sdate + datetime.timedelta(
                                    hours=step-2*int(c.dtime))
                sdates = sdate + datetime.timedelta(hours=step)
            else:
                break

            if c.maxstep > 12:
                fnout = c.inputdir + '/flux' + \
                    sdate.strftime('%Y%m%d') + '.{:0>2}'.format(time/100) + \
                    '.{:0>3}'.format(step-2*int(c.dtime))
                gnout = c.inputdir + '/flux' + \
                    sdate.strftime('%Y%m%d') + '.{:0>2}'.format(time/100) + \
                    '.{:0>3}'.format(step-int(c.dtime))
                hnout = c.inputdir + '/flux' + \
                    sdate.strftime('%Y%m%d') + '.{:0>2}'.format(time/100) + \
                    '.{:0>3}'.format(step)
                g = open(gnout, 'w')
                h = open(hnout, 'w')
            else:
                fnout = c.inputdir + '/flux' + fdate.strftime('%Y%m%d%H')
                gnout = c.inputdir + '/flux' + (fdate+datetime.timedelta(
                    hours = int(c.dtime))).strftime('%Y%m%d%H')
                hnout = c.inputdir + '/flux' + sdates.strftime('%Y%m%d%H')
                g = open(gnout, 'w')
                h = open(hnout, 'w')
            print("outputfile = " + fnout)
            f = open(fnout, 'w')

            # read message for message and store relevant data fields
            # data keywords are stored in pars
            while 1:
                if gid is None:
                    break
                cparamId = str(grib_get(gid, 'paramId'))
                step = grib_get(gid, 'step')
                atime = grib_get(gid, 'time')
                ni = grib_get(gid, 'Ni')
                nj = grib_get(gid, 'Nj')
                if cparamId in valsdict.keys():
                    values = grib_get_values(gid)
                    vdp = valsdict[cparamId]
                    svdp = svalsdict[cparamId]
                    sd = stepsdict[cparamId]

                    if cparamId == '142' or cparamId == '143':
                        fak = 1. / 1000.
                    else:
                        fak = 3600.

                    values = (reshape(values, (nj, ni))).flatten() / fak
                    vdp.append(values[:])  # save the accumulated values
                    if step <= int(c.dtime):
                        svdp.append(values[:] / int(c.dtime))
                    else:  # deaccumulate values
                        svdp.append((vdp[-1] - vdp[-2]) / int(c.dtime))

                    print(cparamId, atime, step, len(values),
                          values[0], std(values))
                    # save the 1/3-hourly or specific values
                    # svdp.append(values[:])
                    sd.append(step)
                    # len(svdp) correspond to the time
                    if len(svdp) >= 3:
                        if len(svdp) > 3:
                            if cparamId == '142' or cparamId == '143':
                                values = Disagg.darain(svdp)
                            else:
                                values = Disagg.dapoly(svdp)

                            if not (step == c.maxstep and c.maxstep > 12 \
                                    or sdates == elimit):
                                vdp.pop(0)
                                svdp.pop(0)
                        else:
                            if c.maxstep > 12:
                                values = svdp[1]
                            else:
                                values = svdp[0]

                        grib_set_values(gid, values)
                        if c.maxstep > 12:
                            grib_set(gid, 'step', max(0, step-2*int(c.dtime)))
                        else:
                            grib_set(gid, 'step', 0)
                            grib_set(gid, 'time', fdate.hour*100)
                            grib_set(gid, 'date', fdate.year*10000 +
                                     fdate.month*100+fdate.day)
                        grib_write(gid, f)

                        if c.basetime is not None:
                            elimit = datetime.datetime.strptime(c.end_date +
                                                                c.basetime,
                                                                '%Y%m%d%H')
                        else:
                            elimit = sdate + datetime.timedelta(2*int(c.dtime))

                        # squeeze out information of last two steps contained
                        # in svdp
                        # if step+int(c.dtime) == c.maxstep and c.maxstep>12
                        # or sdates+datetime.timedelta(hours = int(c.dtime))
                        # >= elimit:
                        # Note that svdp[0] has not been popped in this case

                        if (step == c.maxstep and c.maxstep > 12
                            or sdates == elimit):

                            values = svdp[3]
                            grib_set_values(gid, values)
                            grib_set(gid, 'step', 0)
                            truedatetime = fdate + datetime.timedelta(
                                     hours=2*int(c.dtime))
                            grib_set(gid, 'time', truedatetime.hour * 100)
                            grib_set(gid, 'date', truedatetime.year * 10000 +
                                     truedatetime.month * 100 +
                                     truedatetime.day)
                            grib_write(gid, h)

                            #values = (svdp[1]+svdp[2])/2.
                            if cparamId == '142' or cparamId == '143':
                                values = Disagg.darain(list(reversed(svdp)))
                            else:
                                values = Disagg.dapoly(list(reversed(svdp)))

                            grib_set(gid, 'step',0)
                            truedatetime = fdate + datetime.timedelta(
                                     hours=int(c.dtime))
                            grib_set(gid, 'time', truedatetime.hour * 100)
                            grib_set(gid, 'date', truedatetime.year * 10000 +
                                     truedatetime.month * 100 +
                                     truedatetime.day)
                            grib_set_values(gid, values)
                            grib_write(gid, g)

                    grib_release(gid)

                    gid = grib_new_from_index(iid)

            f.close()
            g.close()
            h.close()

        grib_index_release(iid)

        return
