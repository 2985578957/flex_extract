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

import _config
# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------


def check_grid(grid):

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
    '''


    '''
    if 'N' in grid:  # Gaussian output grid
        area = 'G'
        return area

    # if area was provided decompose area into its 4 components
    if area:
        components = area.split('/')
        upper, left, lower, right = components

    # determine area format
    if (abs(float(upper) / 1000.) >= 0.05 and
        abs(float(lower) / 1000.) >= 0.05 and
        abs(float(left) / 1000.) >= 0.05 and
        abs(float(right) / 1000.) >= 0.05):
        # area is defined in 1/1000 degrees; old format
        area = '{}/{}/{}/{}'.format(float(upper) / 1000.,
                                    float(left) / 1000.,
                                    float(lower) / 1000.,
                                    float(right) / 1000.)
    elif (abs(float(upper) / 1000.) < 0.05 and
          abs(float(lower) / 1000.) < 0.05 and
          abs(float(left) / 1000.) < 0.05 and
          abs(float(right) / 1000.) < 0.05):
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
    '''

    Parameters
    ----------
    par : :obj:``
        ...

    Return
    ------

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


def check_purefc(type):
    '''Check for a pure forecast mode.

    Parameters
    ----------
    type : :obj:`list` of :obj:`string`
        List of field types.

    Return
    ------
    True or False:
        True if pure forecasts are to be retrieved. False if there are
        analysis fields in between.
    '''

    if 'AN' not in type and '4V' not in type:
        # pure forecast
        return True

    return False


def check_():
    '''

    Parameters
    ----------
    par : :obj:``
        ...

    Return
    ------

    '''
    return
