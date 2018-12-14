#!/usr/bin/env python
# -*- coding: utf-8 -*-
##*******************************************************************************
# @Author: Anne Philipp (University of Vienna)
#
# @Date: November 2018
#
# @Change History:
#
# @License:
#    (C) Copyright 2014-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Modul Description:
#
#
# @Module Content:

#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

import os
import _config
import exceptions
from tools import my_error, silent_remove
from datetime import datetime
# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------

def check_logicals_type(c, logicals):
    '''Check that the logical variables have correct type integer.

    Parameters
    ----------
    c : :obj:`ControlFile`
        Contains all the parameters of CONTROL file and
        command line.

    logicals : :obj:`list` of (:obj:`string` or :obj:`integer`)
        Names of the switches that are used to control the flow of the
        program.

    Return
    ------

    '''

    for var in logicals:
        if not isinstance(getattr(c, var), int):
            setattr(c, var, int(getattr(c, var)))

    return

def check_grid(grid):
    '''Convert grid into correct Lat/Lon format. E.g. '0.5/0.5'

    Checks on format of original grid. Wether it is in the order of 1000 or 1.
    Convert to correct grid format and substitute into "Lat/Lon" format string.

    Parameters
    ----------
    grid : :obj:`string`
        Contains grid information

    Return
    ------
    grid : :obj:``string`
        Contains grid in format Lat/lon. E.g. 0.1/0.1
    '''

    if 'N' in grid:
        return grid
    if '/' in grid:
        gridx, gridy = grid.split('/')
        if gridx == gridy:
            grid = gridx
        else:
            raise ValueError('GRID parameter contains two values '
                             'which are unequal %s' (grid))
    # determine grid format
    if float(grid) / 100. >= 0.5:
        # grid is defined in 1/1000 degrees; old format
        grid = '{}/{}'.format(float(grid) / 1000.,
                              float(grid) / 1000.)
    elif float(grid) / 100. < 0.5:
        # grid is defined in normal degree; new format
        grid = '{}/{}'.format(float(grid), float(grid))

    return grid

def check_area(grid, area, upper, lower, left , right):
    '''Defines the correct area string.

    Checks on the format of the four area components. Wether it is of
    the order of 1000 or 1. Also checks wether area was already set by command
    line, then the four components are overwritten.
    Convert to correct format of the order of magnitude "1" and sets the
    area parameter (North/West/South/East).
    E.g.: -5./20./10./10.

    Parameters
    ----------
    grid : :obj:`string`
        Contains grid information.

    area : :obj:`string`
        Contains area informtion.

    upper : :obj:`string`
        The northern most latitude.

    lower : :obj:`string`
        The souther most latitude.

    left : :obj:`string`
        The western most longitude.

    right : :obj:`string`
        The eastern most longiude.

    Return
    ------
    grid : :obj:``string`
        Contains grid in format Lat/lon. E.g. 0.1/0.1
    '''
    if 'N' in grid:  # Gaussian output grid
        area = 'G'
        return area

    # if area was provided decompose area into its 4 components
    if area:
        components = area.split('/')
        upper, left, lower, right = components

    # determine area format
    if ((abs(float(upper) / 10000.) >= 0.01 or float(upper) / 1000. == 0. ) and
        (abs(float(lower) / 10000.) >= 0.01 or float(lower) / 1000. == 0. ) and
        (abs(float(left) / 10000.) >= 0.01 or float(left) / 1000. == 0. ) and
        (abs(float(right) / 10000.) >= 0.01 or float(right) / 1000. == 0.)):
        # area is defined in 1/1000 degrees; old format
        area = '{}/{}/{}/{}'.format(float(upper) / 1000.,
                                    float(left) / 1000.,
                                    float(lower) / 1000.,
                                    float(right) / 1000.)
    elif (abs(float(upper) / 10000.) < 0.05 and
          abs(float(lower) / 10000.) < 0.05 and
          abs(float(left) / 10000.) < 0.05 and
          abs(float(right) / 10000.) < 0.05):
        # area is already in new format
        area = '{}/{}/{}/{}'.format(float(upper),
                                    float(left),
                                    float(lower),
                                    float(right))
    else:
        raise ValueError('The area components have different '
                         'formats (upper, lower, left, right): '
                         '{}/{}/{}/{}'.format(str(upper), str(lower),
                                              str(left) , str(right)))

    return area

def check_levels(levelist, level):
    '''Defines correct level list and guarantees that the maximum level is
    one of the available maximum levels.

    Parameters
    ----------
    levelist : :obj:`string`
        Specifies the level list.
        Examples: model level: 1/to/137, pressure levels: 500/to/1000

    level : :obj:`string`
        Specifies the maximum level.

    Return
    ------
    levelist : :obj:`string`
        Specifies the required levels. It has to have a valid
        correspondence to the selected levtype.
        Examples: model level: 1/to/137, pressure levels: 500/to/1000

    level : :obj:`string`
        Specifies the maximum level. It has to be one of the
        available maximum level number as contained in the variable
        MAX_LEVEL_LIST in "_config". E.g. [16, 19, 31, 40, 50, 60, 62, 91, 137]

    '''
    # assure consistency of levelist and level
    if not levelist and not level:
        raise ValueError('ERROR: neither levelist nor level '
                         'specified in CONTROL file')
    elif not levelist and level:
        levelist = '1/to/' + level
    elif (levelist and not level) or \
         (levelist[-1] != level[-1]):
        level = levelist.split('/')[-1]
    else:
        pass

    # check if max level is a valid level
    if int(level) not in _config.MAX_LEVEL_LIST:
        raise ValueError('ERROR: \n'
                         'LEVEL must be the maximum level of a specified '
                         'level list from ECMWF, e.g. {} \n'
                         'Check parameter "LEVEL" or the max level of '
                         '"LEVELIST"!'.format(str(_config.MAX_LEVEL_LIST)))

    return levelist, level


def check_ppid(c, ppid):
    '''Sets the current PPID.

    Parameters
    ----------
    c : :obj:`ControlFile`
            Contains all the parameters of CONTROL file and
            command line.

    ppid : :obj:`int` or :obj:`None`
        Contains the ppid number provided by the command line parameter
        of is None otherwise.

    Return
    ------

    '''

    if not ppid:
        c.ppid = str(os.getppid())
    else:
        c.ppid = ppid

    return


def check_purefc(ftype):
    '''Check for a pure forecast mode.

    Parameters
    ----------
    ftype : :obj:`list` of :obj:`string`
        List of field types.

    Return
    ------
    True or False:
        True if pure forecasts are to be retrieved. False if there are
        analysis fields in between.
    '''

    if 'AN' not in ftype and '4V' not in ftype:
        # pure forecast
        return 1

    return 0


def check_step(step, mailfail):
    '''Checks on step format and convert into a list of steps.

    If the steps were defined with "to" and "by" they are converted into
    a list of steps. If the steps were set in a string, it is
    converted into a list.

    Parameters
    ----------
    step : :obj:`list` of :obj:`string` or :obj:`string`
        Specifies the forecast time step from forecast base time.
        Valid values are hours (HH) from forecast base time.

    mailfail : :obj:`list` of :obj:``string`
        Contains all email addresses which should be notified.
        It might also contain just the ecmwf user name which will trigger
        mailing to the associated email address for this user.

    Return
    ------
    step : :obj:`list` of :obj:`string`
        List of forecast steps in format e.g. [001, 002, ...]
    '''

    if '/' in step:
        steps = step.split('/')
        if 'to' in step.lower() and 'by' in step.lower():
            ilist = np.arange(int(steps[0]),
                              int(steps[2]) + 1,
                              int(steps[4]))
            step = ['{:0>3}'.format(i) for i in ilist]
        elif 'to' in step.lower() and 'by' not in step.lower():
            my_error(mailfail, step + ':\n' +
                     'if "to" is used in steps parameter, '
                     'please use "by" as well')
        else:
            step = steps

    if not isinstance(step, list):
        step = [step]

    return step

def check_type(ftype, steps):
    '''Check if type variable is of type list and if analysis field has
    forecast step 0.

    Parameters
    ----------
    ftype : :obj:`list` of :obj:`string` or :obj:`string`
        List of field types.

    steps : :obj:`string`
        Specifies the forecast time step from forecast base time.
        Valid values are hours (HH) from forecast base time.

    Return
    ------
    ftype : :obj:`list` of :obj:`string`
        List of field types.
    '''
    if not isinstance(ftype, list):
        ftype = [ftype]

    for i, val in enumerate(ftype):
        if ftype[i] == 'AN' and int(steps[i]) != 0:
            print('Analysis retrievals must have STEP = 0 (now set to 0)')
            ftype[i] = 0

    return ftype

def check_time(ftime):
    '''Check if time variable is of type list. Otherwise convert to list.

    Parameters
    ----------
    ftime : :obj:`list` of :obj:`string` or :obj:`string`
        The time in hours of the field.

    Return
    ------
    ftime : :obj:`list` of :obj:`string`
        The time in hours of the field.
    '''
    if not isinstance(ftime, list):
        ftime = [ftime]

    return ftime

def check_len_type_time_step(ftype, ftime, steps, maxstep, purefc):
    '''Check if

    Parameters
    ----------
    ftype : :obj:`list` of :obj:`string`
        List of field types.

    ftime : :obj:`list` of :obj:`string` or :obj:`string`
        The time in hours of the field.

    steps : :obj:`string`
        Specifies the forecast time step from forecast base time.
        Valid values are hours (HH) from forecast base time.

    maxstep : :obj:`integer`
        The maximum forecast time step in hours from the forecast base time.
        This is the maximum step for non flux (accumulated) forecast data.

    purefc : :obj:`integer`
        Switch for definition of pure forecast mode or not.

    Return
    ------
    ftype : :obj:`list` of :obj:`string`
        List of field types.

    ftime : :obj:`list` of :obj:`string`
        The time in hours of the field.

    steps : :obj:`string`
        Specifies the forecast time step from forecast base time.
        Valid values are hours (HH) from forecast base time.
    '''
    if not (len(ftype) == len(ftime) == len(steps)):
        raise ValueError('ERROR: The number of field types, times and steps '
                         'are not the same! Please check the setting in the '
                         'CONTROL file!')

    # if pure forecast is selected and only one field type/time is set
    # prepare a complete list of type/time/step combination upto maxstep
    if len(ftype) == 1 and purefc:
        ftype = []
        steps = []
        ftime = []
        for i in range(0, maxstep + 1):
            ftype.append(ftype[0])
            steps.append('{:0>3}'.format(i))
            ftime.append(ftime[0])

    return ftype, ftime, steps

def check_mail(mail):
    '''Check the string of mail addresses, seperate them and convert to a list.

    Parameters
    ----------
    mail : :obj:`list` of :obj:`string` or :obj:`string`
        Contains email addresses for notifications.
        It might also contain just the ecmwf user name which will trigger
        mailing to the associated email address for this user.

    Return
    ------
    mail : :obj:`list` of :obj:``string`
        Contains email addresses for notifications.
        It might also contain just the ecmwf user name which will trigger
        mailing to the associated email address for this user.

    '''
    if not isinstance(mail, list):
        if ',' in mail:
            mail = mail.split(',')
        elif ' ' in mail:
            mail = mail.split()
        else:
            mail = [mail]

    return mail

def check_queue(queue, gateway, destination, ecuid, ecgid):
    '''Check if the necessary ECMWF parameters are set if the queue is
    one of the QUEUES_LIST (in _config).

    Parameters
    ----------
    queue : :obj:`string`
        Name of the queue if submitted to the ECMWF servers.
        Used to check if ecuid, ecgid, gateway and destination
        are set correctly and are not empty.

    gateway : :obj:`string`
        The address of the gateway server.

    destination : :obj:`string`
        The name of the destination of the gateway server for data
        transfer through ectrans. E.g. name@genericSftp

    ecuid : :obj:`string`
        ECMWF user id.

    ecgid : :obj:`string`
        ECMWF group id.

    Return
    ------

    '''
    if queue in _config.QUEUES_LIST and \
        not gateway or not destination or \
        not ecuid or not ecgid:
        raise ValueError('\nEnvironment variables GATEWAY, DESTINATION, ECUID '
                         'and ECGID were not set properly! \n '
                         'Please check for existence of file "ECMWF_ENV" '
                         'in the run directory!')
    return

def check_pathes(idir, odir, fpdir, fedir):
    '''Check if output and flexpart pathes are set.

    Parameters
    ----------
    idir : :obj:`string`
        Path to the temporary directory for MARS retrieval data.

    odir : :obj:`string`
        Path to the final output directory where the FLEXPART input files
        will be stored.

    fpdir : :obj:`string`
        Path to FLEXPART root directory.

    fedir : :obj:`string`
        Path to flex_extract root directory.

    Return
    ------
    odir : :obj:`string`
        Path to the final output directory where the FLEXPART input files
        will be stored.

    fpdir : :obj:`string`
        Path to FLEXPART root directory.

    '''
    if not fpdir:
        fpdir = fedir

    if not odir:
        odir = idir

    return odir, fpdir

def check_dates(start, end):
    '''Checks if there is at least a start date for a one day retrieval.

    Checks if end date lies after start date and end date is set.

    Parameters
    ----------
    start : :obj:`string`
        The start date of the retrieval job.

    end : :obj:`string`
        The end date of the retrieval job.

    Return
    ------
    start : :obj:`string`
        The start date of the retrieval job.

    end : :obj:`string`
        The end date of the retrieval job.

    '''
    # check for having at least a starting date
    # otherwise program is not allowed to run
    if not start:
        raise ValueError('start_date was neither specified in command line nor '
                         'in CONTROL file.\n'
                         'Try "{} -h" to print usage information'
                         .format(sys.argv[0].split('/')[-1]) )

    # retrieve just one day if end_date isn't set
    if not end:
        end = start

    dstart = datetime.strptime(start, '%Y%m%d')
    dend = datetime.strptime(end, '%Y%m%d')
    if dstart > dend:
        raise ValueError('ERROR: Start date is after end date! \n'
                         'Please adapt the dates in CONTROL file or '
                         'command line! (start={}; end={})'.format(start, end))

    return start, end

def check_maxstep(maxstep, steps):
    '''Convert maxstep into integer if it is already given. Otherwise, select
    maxstep by going through the steps list.

    Parameters
    ----------
    maxstep : :obj:`string`
        The maximum forecast time step in hours from the forecast base time.
        This is the maximum step for non flux (accumulated) forecast data.

    steps : :obj:`string`
        Specifies the forecast time step from forecast base time.
        Valid values are hours (HH) from forecast base time.

    Return
    ------
    maxstep : :obj:`integer`
        The maximum forecast time step in hours from the forecast base time.
        This is the maximum step for non flux (accumulated) forecast data.

    '''
    # if maxstep wasn't provided
    # search for it in the "step" parameter
    if not maxstep:
        maxstep = 0
        for s in steps:
            if int(s) > maxstep:
                maxstep = int(s)
    else:
        maxstep = int(maxstep)

    return maxstep

def check_basetime(basetime):
    '''Check if basetime is set and contains one of the two
    possible values (0, 12).

    Parameters
    ----------
    basetime : :obj:``
        The time for a half day retrieval. The 12 hours upfront are to be
        retrieved.

    Return
    ------

    '''
    if basetime:
        if int(basetime) != 0 and int(basetime) != 12:
            raise ValueError('ERROR: Basetime has an invalid value '
                             '-> {}'.format(str(basetime)))
    return

def check_request(request, marsfile):
    '''Check if there is an old mars request file and remove it.

    Parameters
    ----------
    request : :obj:`integer`
        Selects the mode of retrieval.
        0: Retrieves the data from ECMWF.
        1: Prints the mars requests to an output file.
        2: Retrieves the data and prints the mars request.

    marsfile : :obj:`string`
        Path to the mars request file.

    Return
    ------

    '''
    if request != 0:
        if os.path.isfile(marsfile):
            silent_remove(marsfile)
    return

def check_public(public, dataset):
    '''Check wether the dataset parameter is set for a
    public data set retrieval.

    Parameters
    ----------
    public : :obj:`ìnteger`
        Specifies if public data are to be retrieved or not.

    dataset : :obj:`string`
        Specific name which identifies the public dataset.

    Return
    ------

    '''
    if public and not dataset:
        raise ValueError('ERROR: If public mars data wants to be retrieved, '
                         'the "dataset"-parameter has to be set too!')
    return

def check_acctype(acctype, ftype):
    '''Guarantees that the accumulation field type is set.

    If not set, it is derivated as in the old method (TYPE[1]).

    Parameters
    ----------
    acctype : :obj:`string`
        The field type for the accumulated forecast fields.

    ftype : :obj:`list` of :obj:`string`
        List of field types.

    Return
    ------
    acctype : :obj:`string`
        The field type for the accumulated forecast fields.
    '''
    if not acctype:
        print('... Control parameter ACCTYPE was not defined.')
        try:
            if len(ftype) == 1 and ftype[0] != 'AN':
                print('Use same field type as for the non-flux fields.')
                acctype = ftype[0]
            elif len(ftype) > 1 and ftype[1] != 'AN':
                print('Use old setting by using TYPE[1] for flux forecast!')
                acctype = ftype[1]
        except:
            raise ValueError('ERROR: Accumulation field type could not be set!')
    else:
        if acctype.upper() == 'AN':
            raise ValueError('ERROR: Accumulation forecast fields can not be '
                             'of type "analysis"!')
    return acctype


def check_acctime(acctime, acctype, purefc):
    '''Guarantees that the accumulation forecast times were set.

    If it is not set, it is tried to set the value fore some of the
    most commonly used data sets. Otherwise it raises an error.

    Parameters
    ----------
    acctime : :obj:`string`
        The starting time from the accumulated forecasts.

    acctype : :obj:`string`
        The field type for the accumulated forecast fields.

    purefc : :obj:`integer`
        Switch for definition of pure forecast mode or not.

    Return
    ------
    acctime : :obj:`string`
        The starting time from the accumulated forecasts.
    '''
    if not acctime:
        print('... Control parameter ACCTIME was not defined.')
        print('... Value will be set depending on field type: '
              '\t\t EA=06/18\n\t\t EI/OD=00/12\n\t\t  EP=18')
        if acctype.upper() == 'EA': # Era 5
            acctime = '06/18'
        elif acctype.upper() == 'EI': # Era-Interim
            acctime = '00/12'
        elif acctype.upper() == 'EP': # CERA
            acctime = '18'
        elif acctype.upper() == 'OD' and not purefc: # On-demand operational
            acctime = '00/12'
        else:
            raise ValueError('ERROR: Accumulation forecast time can not '
                             'automatically be derived!')
    return acctime

def check_accmaxstep(accmaxstep, acctype, purefc, maxstep):
    '''Guarantees that the accumulation forecast step were set.

    Parameters
    ----------
    accmaxstep : :obj:`string`
        The maximum forecast step for the accumulated forecast fields.

    acctype : :obj:`string`
        The field type for the accumulated forecast fields.

    purefc : :obj:`integer`
        Switch for definition of pure forecast mode or not.

    maxstep : :obj:`string`
        The maximum forecast time step in hours from the forecast base time.
        This is the maximum step for non flux (accumulated) forecast data.

    Return
    ------
    accmaxstep : :obj:`string`
        The maximum forecast step for the accumulated forecast fields.
    '''
    if not accmaxstep:
        print('... Control parameter ACCMAXSTEP was not defined.')
        print('... Value will be set depending on field type/time: '
              '\t\t EA/EI/OD=12\n\t\t  EP=24')
        if acctype.upper() in ['EA', 'EI', 'OD'] and not purefc:
            # Era 5, Era-Interim, On-demand operational
            accmaxstep = '12'
        elif acctype.upper() == 'EP': # CERA
            accmaxstep = '18'
        elif purefc and accmaxstep != maxstep:
            accmaxstep = maxstep
            print('... For pure forecast mode, the accumulated forecast must '
                  'have the same maxstep as the normal forecast fields!\n'
                  '\t\t Accmaxstep was set to maxstep!')
        else:
            raise ValueError('ERROR: Accumulation forecast step can not '
                             'automatically be derived!')
    else:
        if purefc and int(accmaxstep) != int(maxstep):
            accmaxstep = maxstep
            print('... For pure forecast mode, the accumulated forecast must '
                          'have the same maxstep as the normal forecast fields!\n'
                          '\t\t Accmaxstep was set to maxstep!')
    return accmaxstep

def check_addpar(addpar):
    '''Check that addpar has correct format of additional parameters in
    a single string, so that it can be easily appended to the hard coded
    parameters that are retrieved in any case.

    Parameters
    ----------
    addpar : :obj:`string` or :obj:'list' of :obj:'string'
        List of additional parameters to be retrieved.

    Return
    ------
    addpar : :obj:'string'
        List of additional parameters to be retrieved.
    '''

    if addpar and isinstance(addpar, str):
        if '/' in addpar:
            parlist = addpar.split('/')
            parlist = [p for p in parlist if p is not '']
        else:
            parlist = [addpar]

        addpar = '/' + '/'.join(parlist)

    return addpar


def check_job_chunk(job_chunk):
    '''Checks that the job chunk number is positive and non zero.

    Parameters
    ----------
    job_chunk : :obj:`integer`
        The number of days for a single job script.

    Return
    ------
    job_chunk : :obj:`integer`
        The number of days for a single job script.
    '''
    if job_chunk < 0:
        raise ValueError('ERROR: The number of job chunk is negative!\n'
                         'It has to be a positive number!')
    elif job_chunk == 0:
        job_chunk = None
    else:
        pass

    return job_chunk
