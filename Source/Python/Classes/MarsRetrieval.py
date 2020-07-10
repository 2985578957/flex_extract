#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Fouilloux (University of Oslo)
#
# @Date: October 2014
#
# @Change History:
#
#   November 2015 - Leopold Haimberger (University of Vienna):
#        - optimized display_info
#        - optimized data_retrieve and seperate between python and shell
#          script call
#
#   February 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added documentation
#        - applied some minor modifications in programming style/structure
#        - added writing of mars request attributes to a csv file
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
import subprocess
import traceback

# software specific classes and modules from flex_extract
#pylint: disable=wrong-import-position
sys.path.append('../')
import _config
#pylint: disable=invalid-name
try:
    ec_api = True
    import ecmwfapi
except ImportError:
    ec_api = False

try:
    cds_api = True
    import cdsapi
except ImportError:
    cds_api = False
#pylint: enable=invalid-name
#pylint: enable=wrong-import-position
# ------------------------------------------------------------------------------
# CLASS
# ------------------------------------------------------------------------------
class MarsRetrieval(object):
    '''Specific syntax and content for submission of MARS retrievals.

    A MARS revtrieval has a specific syntax with a selection of keywords and
    their corresponding values. This class provides the necessary functions
    by displaying the selected parameters and their values and the actual
    retrievement of the data through a mars request or a Python web api
    interface. The initialization already expects all the keyword values.

    A description of MARS keywords/arguments and examples of their
    values can be found here:
    https://software.ecmwf.int/wiki/display/UDOC/\
                   Identification+keywords#Identificationkeywords-class

    Attributes
    ----------
    server : ECMWFService or ECMWFDataServer
        This is the connection to the ECMWF data servers.

    public : int
        Decides which Web API Server version is used.

    marsclass : str, optional
        Characterisation of dataset.

    dataset : str, optional
        For public datasets there is the specific naming and parameter
        dataset which has to be used to characterize the type of
        data.

    type : str, optional
        Determines the type of fields to be retrieved.

    levtype : str, optional
        Denotes type of level.

    levelist : str, optional
        Specifies the required levels.

    repres : str, optional
        Selects the representation of the archived data.

    date : str, optional
        Specifies the Analysis date, the Forecast base date or
        Observations date.

    resol : str, optional
        Specifies the desired triangular truncation of retrieved data,
        before carrying out any other selected post-processing.

    stream : str, optional
        Identifies the forecasting system used to generate the data.

    area : str, optional
        Specifies the desired sub-area of data to be extracted.

    time : str, optional
        Specifies the time of the data in hours and minutes.

    step : str, optional
        Specifies the forecast time step from forecast base time.

    expver : str, optional
        The version of the dataset.

    number : str, optional
        Selects the member in ensemble forecast run.

    accuracy : str, optional
        Specifies the number of bits per value to be used in the
        generated GRIB coded fields.

    grid : str, optional
        Specifies the output grid which can be either a Gaussian grid
        or a Latitude/Longitude grid.

    gaussian : str, optional
        This parameter is deprecated and should no longer be used.
        Specifies the desired type of Gaussian grid for the output.

    target : str, optional
        Specifies a file into which data is to be written after
        retrieval or manipulation.

    param : str, optional
        Specifies the meteorological parameter.
    '''

    def __init__(self, server, public, marsclass="EA", dataset="", type="",
                 levtype="", levelist="", repres="", date="", resol="",
                 stream="", area="", time="", step="", expver="1",
                 number="", accuracy="", grid="", gaussian="", target="",
                 param=""):
        '''Initialises the instance of the MarsRetrieval class and
        defines and assigns a set of the necessary retrieval parameters
        for the FLEXPART input data.
        A description of MARS keywords/arguments, their dependencies
        on each other and examples of their values can be found here:

        https://software.ecmwf.int/wiki/display/UDOC/MARS+keywords

        Parameters
        ----------
        server : ECMWFService or ECMWFDataServer
            This is the connection to the ECMWF data servers.
            It is needed for the pythonic access of ECMWF data.

        public : int
            Decides which Web API version is used:
            0: member-state users and full archive access
            1: public access and limited access to the public server and
               datasets. Needs the parameter dataset.
            Default is "0" and for member-state users.

        marsclass : str, optional
            Characterisation of dataset. E.g. EI (ERA-Interim),
            E4 (ERA40), OD (Operational archive), EA (ERA5).
            Default is the ERA5 dataset "EA".

        dataset : str, optional
            For public datasets there is the specific naming and parameter
            dataset which has to be used to characterize the type of
            data. Usually there is less data available, either in times,
            domain or parameter.
            Default is an empty string.

        type : str, optional
            Determines the type of fields to be retrieved.
            Selects between observations, images or fields.
            Examples for fields: Analysis (an), Forecast (fc),
            Perturbed Forecast (pf), Control Forecast (cf) and so on.
            Default is an empty string.

        levtype : str, optional
            Denotes type of level. Has a direct implication on valid
            levelist values!
            E.g. model level (ml), pressure level (pl), surface (sfc),
            potential vorticity (pv), potential temperature (pt)
            and depth (dp).
            Default is an empty string.

        levelist : str, optional
            Specifies the required levels. It has to have a valid
            correspondence to the selected levtype.
            Examples: model level: 1/to/137, pressure levels: 500/to/1000
            Default is an empty string.

        repres : str, optional
            Selects the representation of the archived data.
            E.g. sh - spherical harmonics, gg - Gaussian grid,
            ll - latitude/longitude, ...
            Default is an empty string.

        date : str, optional
            Specifies the Analysis date, the Forecast base date or
            Observations date. Valid formats are:
            Absolute as YYYY-MM-DD or YYYYMMDD.
            Default is an empty string.

        resol : str, optional
            Specifies the desired triangular truncation of retrieved data,
            before carrying out any other selected post-processing.
            The default is automatic truncation (auto), by which the lowest
            resolution compatible with the value specified in grid is
            automatically selected for the retrieval.
            Users wanting to perform post-processing from full spectral
            resolution should specify Archived Value (av).
            The following are examples of existing resolutions found in
            the archive: 63, 106, 159, 213, 255, 319, 399, 511, 799 or 1279.
            This keyword has no meaning/effect if the archived data is
            not in spherical harmonics representation.
            The best selection can be found here:
            https://software.ecmwf.int/wiki/display/UDOC/\
                  Retrieve#Retrieve-Truncationbeforeinterpolation
            Default is an empty string.

        stream : str, optional
            Identifies the forecasting system used to generate the data.
            E.g. oper (Atmospheric model), enfo (Ensemble forecats), ...
            Default is an empty string.

        area : str, optional
            Specifies the desired sub-area of data to be extracted.
            Areas can be defined to wrap around the globe.

            Latitude values must be given as signed numbers, with:
                north latitudes (i.e. north of the equator)
                    being positive (e.g: 40.5)
                south latitutes (i.e. south of the equator)
                    being negative (e.g: -50.5)
            Longtitude values must be given as signed numbers, with:
                east longitudes (i.e. east of the 0 degree meridian)
                    being positive (e.g: 35.0)
                west longitudes (i.e. west of the 0 degree meridian)
                    being negative (e.g: -20.5)

            E.g.: North/West/South/East
            Default is an empty string.

        time : str, optional
            Specifies the time of the data in hours and minutes.
            Valid values depend on the type of data: Analysis time,
            Forecast base time or First guess verification time
            (all usually at synoptic hours: 00, 06, 12 and 18 ).
            Observation time (any combination in hours and minutes is valid,
            subject to data availability in the archive).
            The syntax is HHMM or HH:MM. If MM is omitted it defaults to 00.
            Default is an empty string.

        step : str, optional
            Specifies the forecast time step from forecast base time.
            Valid values are hours (HH) from forecast base time. It also
            specifies the length of the forecast which verifies at
            First Guess time.
            E.g. 1/3/6-hourly
            Default is an empty string.

        expver : str, optional
            The version of the dataset. Each experiment is assigned a
            unique code (version). Production data is assigned 1 or 2,
            and experimental data in Operations 11, 12 ,...
            Research or Member State's experiments have a four letter
            experiment identifier.
            Default is "1".

        number : str, optional
            Selects the member in ensemble forecast run. (Only then it
            is necessary.) It has a different meaning depending on
            the type of data.
            E.g. Perturbed Forecasts: specifies the Ensemble forecast member
            Default is an empty string.

        accuracy : str, optional
            Specifies the number of bits per value to be used in the
            generated GRIB coded fields.
            A positive integer may be given to specify the preferred number
            of bits per packed value. This must not be greater than the
            number of bits normally used for a Fortran integer on the
            processor handling the request (typically 32 or 64 bit).
            Within a compute request the accuracy of the original fields
            can be passed to the result field by specifying accuracy=av.
            Default is an empty string.

        grid : str, optional
            Specifies the output grid which can be either a Gaussian grid
            or a Latitude/Longitude grid. MARS requests specifying
            grid=av will return the archived model grid.

            Lat/Lon grid: The grid spacing needs to be an integer
            fraction of 90 degrees e.g. grid = 0.5/0.5

            Gaussian grid: specified by a letter denoting the type of
            Gaussian grid followed by an integer (the grid number)
            representing the number of lines between the Pole and Equator,
            e.g.
            grid = F160 - full (or regular) Gaussian grid with
                   160 latitude lines between the pole and equator
            grid = N320 - ECMWF original reduced Gaussian grid with
                   320 latitude lines between the pole and equator,
                   see Reduced Gaussian Grids for grid numbers used at ECMWF
            grid = O640 - ECMWF octahedral (reduced) Gaussian grid with
                   640 latitude lines between the pole and equator
            Default is an empty string.

        gaussian : str, optional
            This parameter is deprecated and should no longer be used.
            Specifies the desired type of Gaussian grid for the output.
            Valid Gaussian grids are quasi-regular (reduced) or regular.
            Keyword gaussian can only be specified together with
            keyword grid. Gaussian without grid has no effect.
            Default is an empty string.

        target : str, optional
            Specifies a file into which data is to be written after
            retrieval or manipulation. Path names should always be
            enclosed in double quotes. The MARS client supports automatic
            generation of multiple target files using MARS keywords
            enclosed in square brackets [ ].  If the environment variable
            MARS_MULTITARGET_STRICT_FORMAT is set to 1 before calling mars,
            the keyword values will be used in the filename as shown by
            the ecCodes GRIB tool grib_ls -m, e.g. with
            MARS_MULTITARGET_STRICT_FORMAT set to 1 the keywords time,
            expver and param will be formatted as 0600, 0001 and 129.128
            rather than 600, 1 and 129.
            Default is an empty string.

        param : str, optional
            Specifies the meteorological parameter.
            The list of meteorological parameters in MARS is extensive.
            Their availability is directly related to their meteorological
            meaning and, therefore, the rest of directives specified
            in the MARS request.
            Meteorological parameters can be specified by their
            GRIB code (param=130), their mnemonic (param=t) or
            full name (param=temperature).
            The list of parameter should be seperated by a "/"-sign.
            E.g. 130/131/133
            Default is an empty string.

        Return
        ------

        '''

        self.server = server
        self.public = public
        self.marsclass = marsclass
        self.dataset = dataset
        self.type = type
        self.levtype = levtype
        self.levelist = levelist
        self.repres = repres
        self.date = date
        self.resol = resol
        self.stream = stream
        self.area = area
        self.time = time
        self.step = step
        self.expver = expver
        self.number = number
        self.accuracy = accuracy
        self.grid = grid
        self.gaussian = gaussian
        self.target = target
        self.param = param

        return


    def display_info(self):
        '''Prints all class attributes and their values to the
        standard output.

        Parameters
        ----------

        Return
        ------

        '''
        # Get all class attributes and their values as a dictionary
        attrs = vars(self).copy()

        # iterate through all attributes and print them
        # with their corresponding values
        for item in attrs.items():
            if item[0] in ['server', 'public']:
                pass
            else:
                print(item[0] + ': ' + str(item[1]))

        return


    def print_infodata_csv(self, inputdir, request_number):
        '''Write all request parameter in alpabetical order into a "csv" file.

        Parameters
        ----------
        inputdir : str
            The path where all data from the retrievals are stored.

        request_number : int
            Number of mars requests for flux and non-flux data.

        Return
        ------

        '''

        # Get all class attributes and their values as a dictionary
        attrs = vars(self).copy()
        del attrs['server']
        del attrs['public']

        # open a file to store all requests to
        with open(os.path.join(inputdir,
                               _config.FILE_MARS_REQUESTS), 'a') as f:
            f.write(str(request_number) + ', ')
            f.write(', '.join(str(attrs[key])
                              for key in sorted(attrs.keys())))
            f.write('\n')

        return
    
    def _convert_to_cdsera5_sfc_request(self, attrs):
        '''
        The keywords and values for the single level download
        with CDS API is different from MARS. This function 
        converts the old request keywords to the new ones.
        
        Example request for single level downloads in CDS API
        
        retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': 'total_precipitation',
                'year': '2019',
                'month': '01',
                'day': '01',
                'time': '00:00',
                'format': 'grib',
                'grid':[1.0, 1.0],
                'area': [
                    45, 0, 43,
                    12,
                ],
            },
            'download.grib')
            
        Parameters
        ----------
        attrs : dict
            Dictionary of the mars request parameters.

        Return
        ------

        '''
        from datetime import datetime, timedelta
        newattrs = {}

        if '/' in attrs['date']:
            year = set()
            month = set()
            day = set()
            start,end = attrs['date'].split('/')[::2]
            sdate = datetime.strptime(start, '%Y%m%d')
            edate = datetime.strptime(end, '%Y%m%d')
            date = sdate
            while date <= edate:
                year.add(date.year)
                month.add(date.month)
                day.add(date.day)      
                date = date + timedelta(days=1)
            newattrs['year'] =list(year)
            newattrs['month'] = list(month)
            newattrs['day'] =  list(day)                       
        else:
            date = datetime.strptime(attrs['date'], '%Y%m%d')
            newattrs['year'] = date.year
            newattrs['month'] = date.month
            newattrs['day'] =  date.day                  
        
        newattrs['product_type'] = 'reanalysis'
        newattrs['area'] = attrs['area'].split('/')
        newattrs['grid'] = list(map(float,attrs['grid'].split('/')))
        newattrs['param'] = attrs['param'].split('/')        
        newattrs['time'] = list(map(str,range(0,24,3)))
        newattrs['format'] = 'grib'
                
        return newattrs

    def data_retrieve(self):
        '''Submits a MARS retrieval. Depending on the existence of
        ECMWF Web-API or CDS API it is submitted via Python or a
        subprocess in the Shell. The parameter for the mars retrieval
        are taken from the defined class attributes.

        Parameters
        ----------

        Return
        ------

        '''
        # Get all class attributes and their values as a dictionary
        attrs = vars(self).copy()

        # eliminate unnecessary attributes from the dictionary attrs
        del attrs['server']
        del attrs['public']

        # exchange parameter name for marsclass
        mclass = attrs.get('marsclass')
        del attrs['marsclass']
        attrs['class'] = mclass

        # prepare target variable as needed for the Web API or CDS API mode
        # within the dictionary for full access
        # as a single variable for public access
        target = attrs.get('target')
        if not int(self.public):
            del attrs['target']
        print('target: ' + target)
        
        # find all keys without a value and convert all other values to strings
        empty_keys = []
        for key, value in attrs.items():
            if value == '':
                empty_keys.append(str(key))
            else:
                attrs[key] = str(value)

        # delete all empty parameter from the dictionary
        for key in empty_keys:
            del attrs[key]

#        attrs['ppengine'] = 'emos'

        # MARS request via Python script
        if self.server:
            try:
                if cds_api and isinstance(self.server, cdsapi.Client):
                    # distinguish between model (ECMWF MARS access) 
                    # and surface level (CS3 online access)
                    if attrs['levtype'].lower() == 'ml':
                        dataset = _config.CDS_DATASET_ML
                    else:
                        dataset = _config.CDS_DATASET_SFC
                        attrs = self._convert_to_cdsera5_sfc_request(attrs)
                    print('RETRIEVE ERA5 WITH CDS API!')
                    self.server.retrieve(dataset,
                                         attrs, target)
                elif ec_api and isinstance(self.server, ecmwfapi.ECMWFDataServer):
                    print('RETRIEVE PUBLIC DATA (NOT ERA5)!')
                    self.server.retrieve(attrs)
                elif ec_api and isinstance(self.server, ecmwfapi.ECMWFService):
                    print('EXECUTE NON-PUBLIC RETRIEVAL (NOT ERA5)!')
                    self.server.execute(attrs, target)
                else:
                    print('ERROR:')
                    print('No match for Web API instance!')
                    raise IOError
            except Exception as e:
                print('\n\nMARS Request failed!')
                print(e)
                print(traceback.format_exc())
                sys.exit()

        # MARS request via call in shell
        else:
            request_str = 'ret'
            for key, value in attrs.items():
                request_str = request_str + ',' + key + '=' + str(value)
            request_str += ',target="' + target + '"'
            p = subprocess.Popen(['mars'], #'-e'],
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 bufsize=1)
            pout = p.communicate(input=request_str.encode())[0]
            print(pout.decode())

            if 'Some errors reported' in pout.decode():
                print('MARS Request failed - please check request')
                raise IOError
            elif os.stat(target).st_size == 0:
                print('MARS Request returned no data - please check request')
                raise IOError

        return
