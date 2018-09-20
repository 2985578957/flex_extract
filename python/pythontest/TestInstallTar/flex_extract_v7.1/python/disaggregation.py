#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# @Author: Anne Philipp (University of Vienna)
#
# @Date: March 2018
#
# @Change History:
#
#    November 2015 - Leopold Haimberger (University of Vienna):
#        - migration of the methods dapoly and darain from Fortran
#          (flex_extract_v6 and earlier) to Python
#
#    April 2018 - Anne Philipp (University of Vienna):
#        - applied PEP8 style guide
#        - added structured documentation
#        - outsourced the disaggregation functions dapoly and darain
#          to a new module named disaggregation
#
# @License:
#    (C) Copyright 2015-2018.
#
#    This software is licensed under the terms of the Apache Licence Version 2.0
#    which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# @Module Description:
#    disaggregation of deaccumulated flux data from an ECMWF model FG field.
#    Initially the flux data to be concerned are:
#    - large-scale precipitation
#    - convective precipitation
#    - surface sensible heat flux
#    - surface solar radiation
#    - u stress
#    - v stress
#    Different versions of disaggregation is provided for rainfall
#    data (darain, modified linear) and the surface fluxes and
#    stress data (dapoly, cubic polynomial).
#
# @Module Content:
#    - dapoly
#    - darain
#
#*******************************************************************************

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
def dapoly(alist):
    '''
    @Author: P. JAMES

    @Date: 2000-03-29

    @ChangeHistory:
        June 2003     - A. BECK (2003-06-01)
            adaptaions
        November 2015 - Leopold Haimberger (University of Vienna)
            migration from Fortran to Python

    @Description:
        Interpolation of deaccumulated fluxes of an ECMWF model FG field
        using a cubic polynomial solution which conserves the integrals
        of the fluxes within each timespan.
        disaggregationregation is done for 4 accumluated timespans which generates
        a new, disaggregated value which is output at the central point
        of the 4 accumulation timespans. This new point is used for linear
        interpolation of the complete timeseries afterwards.

    @Input:
        alist: list of size 4, array(2D), type=float
            List of 4 timespans as 2-dimensional, horizontal fields.
            E.g. [[array_t1], [array_t2], [array_t3], [array_t4]]

    @Return:
        nfield: array(2D), type=float
            New field which replaces the field at the second position
            of the accumulation timespans.

    '''
    pya = (alist[3] - alist[0] + 3. * (alist[1] - alist[2])) / 6.
    pyb = (alist[2] + alist[0]) / 2. - alist[1] - 9. * pya / 2.
    pyc = alist[1] - alist[0] - 7. * pya / 2. - 2. * pyb
    pyd = alist[0] - pya / 4. - pyb / 3. - pyc / 2.
    nfield = 8. * pya + 4. * pyb + 2. * pyc + pyd

    return nfield


def darain(alist):
    '''
    @Author: P. JAMES

    @Date: 2000-03-29

    @ChangeHistory:
        June 2003     - A. BECK (2003-06-01)
            adaptaions
        November 2015 - Leopold Haimberger (University of Vienna)
            migration from Fortran to Python

    @Description:
        Interpolation of deaccumulated fluxes of an ECMWF model FG rainfall
        field using a modified linear solution which conserves the integrals
        of the fluxes within each timespan.
        disaggregationregation is done for 4 accumluated timespans which generates
        a new, disaggregated value which is output at the central point
        of the 4 accumulation timespans. This new point is used for linear
        interpolation of the complete timeseries afterwards.

    @Input:
        alist: list of size 4, array(2D), type=float
            List of 4 timespans as 2-dimensional, horizontal fields.
            E.g. [[array_t1], [array_t2], [array_t3], [array_t4]]

    @Return:
        nfield: array(2D), type=float
            New field which replaces the field at the second position
            of the accumulation timespans.
    '''
    xa = alist[0]
    xb = alist[1]
    xc = alist[2]
    xd = alist[3]
    xa[xa < 0.] = 0.
    xb[xb < 0.] = 0.
    xc[xc < 0.] = 0.
    xd[xd < 0.] = 0.

    xac = 0.5 * xb
    mask = xa + xc > 0.
    xac[mask] = xb[mask] * xc[mask] / (xa[mask] + xc[mask])
    xbd = 0.5 * xc
    mask = xb + xd > 0.
    xbd[mask] = xb[mask] * xc[mask] / (xb[mask] + xd[mask])
    nfield = xac + xbd

    return nfield
