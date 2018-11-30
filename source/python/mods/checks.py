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


# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------


def check_grid_area(grid, area, upper, lower, left , right):
    '''


    '''
    # if area was provided
    # decompose area into its 4 components
    if area:
        components = area.split('/')
        upper, left, lower, right = components

    if 'N' in grid:  # Gaussian output grid
        area = 'G'
        return grid, area

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

    # determine area format
    if (float(upper) / 1000. >= 0.05 and
        float(lower) / 1000. >= 0.05 and
        float(left) / 1000. >= 0.05 and
        float(right) / 1000. >= 0.05):
        # area is defined in 1/1000 degrees; old format
        area = '{}/{}/{}/{}'.format(float(upper) / 1000.,
                                    float(left) / 1000.,
                                    float(lower) / 1000.,
                                    float(right) / 1000.)
    elif (float(upper) / 1000. < 0.05 and
          float(lower) / 1000. < 0.05 and
          float(left) / 1000. < 0.05 and
          float(right) / 1000. < 0.05):
        # area is already in new format
        area = '{}/{}/{}/{}'.format(float(upper),
                                    float(left),
                                    float(lower),
                                    float(right))
    else:
        raise ValueError('The area components have different '
                         'formats: %s ' (area))

    return grid, area