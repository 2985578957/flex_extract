#!/usr/bin/env python3
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
#        - added the new disaggregation method for precipitation
#
#    June 2020 - Anne Philipp (University of Vienna):
#        - reformulated formular for dapoly
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
#
# @Methods:
#    - dapoly
#    - darain
#    - IA3
#*******************************************************************************
'''Disaggregation of deaccumulated flux data from an ECMWF model FG field.

Initially the flux data to be concerned are:
    - large-scale precipitation
    - convective precipitation
    - surface sensible heat flux
    - surface solar radiation
    - u stress
    - v stress

Different versions of disaggregation is provided for rainfall
data (darain, modified linear) and the surface fluxes and
stress data (dapoly, cubic polynomial).
'''

# ------------------------------------------------------------------------------
# MODULES
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# FUNCTIONS
# ------------------------------------------------------------------------------
def dapoly(alist):
    """Cubic polynomial interpolation of deaccumulated fluxes.

    Interpolation of deaccumulated fluxes of an ECMWF model FG field
    using a cubic polynomial solution which conserves the integrals
    of the fluxes within each timespan.
    Disaggregation is done for 4 accumluated timespans which
    generates a new, disaggregated value which is output at the
    central point of the 4 accumulation timespans.
    This new point is used for linear interpolation of the complete
    timeseries afterwards.

    Parameters
    ----------
    alist : list of array of float
        List of 4 timespans as 2-dimensional, horizontal fields.
        E.g. [[array_t1], [array_t2], [array_t3], [array_t4]]

    Return
    ------
    nfield : array of float
        Interpolated flux at central point of accumulation timespan.

    Note
    ----
    March 2000    : P. JAMES
        Original author

    June 2003     : A. BECK
        Adaptations

    November 2015 : Leopold Haimberger (University of Vienna)
        Migration from Fortran to Python

    """
    
    nfield = -1./12.*alist[0] + \
              7./12.*alist[1] + \
              7./12.*alist[2] - \
              1./12.*alist[3]

    return nfield


def darain(alist):
    """Linear interpolation of deaccumulated fluxes.

    Interpolation of deaccumulated fluxes of an ECMWF model FG rainfall
    field using a modified linear solution which conserves the integrals
    of the fluxes within each timespan.
    Disaggregation is done for 4 accumluated timespans which generates
    a new, disaggregated value which is output at the central point
    of the 4 accumulation timespans. This new point is used for linear
    interpolation of the complete timeseries afterwards.

    Parameters
    ----------
    alist : list of array of float
        List of 4 timespans as 2-dimensional, horizontal fields.
        E.g. [[array_t1], [array_t2], [array_t3], [array_t4]]

    Return
    ------
    nfield : array of float
        Interpolated flux at central point of accumulation timespan.

    Note
    ----
    March 2000    : P. JAMES
        Original author

    June 2003     : A. BECK
        Adaptations

    November 2015 : Leopold Haimberger (University of Vienna)
        Migration from Fortran to Python
    """

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

def IA3(g):
    """ Interpolation with a non-negative geometric mean based algorithm.

    The original grid is reconstructed by adding two sampling points in each
    data series interval. This subgrid is used to keep all information during
    the interpolation within the associated interval. Additionally, an advanced
    monotonicity filter is applied to improve the monotonicity properties of
    the series.

    Note
    ----
    (C) Copyright 2017-2019
    Sabine Hittmeir, Anne Philipp, Petra Seibert

    This work is licensed under the Creative Commons Attribution 4.0
    International License. To view a copy of this license, visit
    http://creativecommons.org/licenses/by/4.0/ or send a letter to
    Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

    Parameters
    ----------
    g : list of float
        Complete data series that will be interpolated having
        the dimension of the original raw series.

    Return
    ------
    f : list of float
        The interpolated data series with additional subgrid points.
        Its dimension is equal to the length of the input data series
        times three.


    References
    ----------
    For more information see article:
    Hittmeir, S.; Philipp, A.; Seibert, P. (2017): A conservative
    interpolation scheme for extensive quantities with application to the
    Lagrangian particle dispersion model FLEXPART.,
    Geoscientific Model Development
    """

    #######################  variable description #############################
    #                                                                         #
    # i      - index variable for looping over the data series                #
    # g      - input data series                                              #
    # f      - interpolated and filtered data series with additional          #
    #          grid points                                                    #
    # fi     - function value at position i, f_i                              #
    # fi1    - first  sub-grid function value f_i^1                           #
    # fi2    - second sub-grid function value f_i^2                           #
    # fip1   - next function value at position i+1, f_(i+1)                   #
    # dt     - time step                                                      #
    # fmon   - monotonicity filter                                            #
    #                                                                         #
    ###########################################################################


    import numpy as np

    # time step
    dt = 1.0

    ############### Non-negative Geometric Mean Based Algorithm ###############

    # for the left boundary the following boundary condition is valid:
    # the value at t=0 of the interpolation algorithm coincides with the
    # first data value according to the persistence hypothesis
    f = [g[0]]

    # compute two first sub-grid intervals without monotonicity check
    # go through the data series and extend each interval by two sub-grid
    # points and interpolate the corresponding data values
    # except for the last interval due to boundary conditions
    for i in range(0, 2):

        # as a requirement:
        # if there is a zero data value such that g[i]=0, then the whole
        # interval in f has to be zero to such that f[i+1]=f[i+2]=f[i+3]=0
        # according to Eq. (6)
        if g[i] == 0.:
            f.extend([0., 0., 0.])

        # otherwise the sub-grid values are calculated and added to the list
        else:
            # temporal save of last value in interpolated list
            # since it is the left boundary and hence the new (fi) value
            fi = f[-1]

            # the value at the end of the interval (fip1) is prescribed by the
            # geometric mean, restricted such that non-negativity is guaranteed
            # according to Eq. (25)
            fip1 = min(3. * g[i], 3. * g[i + 1], np.sqrt(g[i + 1] * g[i]))

            # the function value at the first sub-grid point (fi1) is determined
            # according to the equal area condition with Eq. (19)
            fi1 = 3./2.*g[i]-5./12.*fip1-1./12.*fi

            # the function value at the second sub-grid point (fi2) is determined
            # according Eq. (18)
            fi2 = fi1+1./3.*(fip1-fi)

            # add next interval of interpolated (sub-)grid values
            f.append(fi1)
            f.append(fi2)
            f.append(fip1)

    # compute rest of the data series intervals
    # go through the data series and extend each interval by two sub-grid
    # points and interpolate the corresponding data values
    # except for the last interval due to boundary conditions
    for i in range(2, len(g)-1):

        # as a requirement:
        # if there is a zero data value such that g[i]=0, then the whole
        # interval in f has to be zero to such that f[i+1]=f[i+2]=f[i+3]=0
        # according to Eq. (6)
        if g[i] == 0.:
            # apply monotonicity filter for interval before
            # check if there is "M" or "W" shape
            if     np.sign(f[-5]-f[-6]) * np.sign(f[-4]-f[-5]) == -1 \
               and np.sign(f[-4]-f[-5]) * np.sign(f[-3]-f[-4]) == -1 \
               and np.sign(f[-3]-f[-4]) * np.sign(f[-2]-f[-3]) == -1:

                # the monotonicity filter corrects the value at (fim1) by
                # substituting (fim1) with (fmon), see Eq. (27), (28) and (29)
                fmon = min(3. * g[i - 2],
                           3. * g[i - 1],
                           np.sqrt(max(0, (18. / 13. * g[i - 2] - 5. / 13. * f[-7]) *
                                       (18. / 13. * g[i - 1] - 5. / 13. * f[-1]))))

                # recomputation of the sub-grid interval values while the
                # interval boundaries (fi) and (fip2) remains unchanged
                # see Eq. (18) and (19)
                f[-4] = fmon
                f[-6] = 3./2.*g[i-2]-5./12.*fmon-1./12.*f[-7]
                f[-5] = f[-6]+(fmon-f[-7])/3.
                f[-3] = 3./2.*g[i-1]-5./12.*f[-1]-1./12.*fmon
                f[-2] = f[-3]+(f[-1]-fmon)/3.

            f.extend([0., 0., 0.])

        # otherwise the sub-grid values are calculated and added to the list
        else:
            # temporal save of last value in interpolated list
            # since it is the left boundary and hence the new (fi) value
            fi = f[-1]

            # the value at the end of the interval (fip1) is prescribed by the
            # geometric mean, restricted such that non-negativity is guaranteed
            # according to Eq. (25)
            fip1 = min(3. * g[i], 3. * g[i + 1], np.sqrt(g[i + 1] * g[i]))

            # the function value at the first sub-grid point (fi1) is determined
            # according to the equal area condition with Eq. (19)
            fi1 = 3./2.*g[i]-5./12.*fip1-1./12.*fi

            # the function value at the second sub-grid point (fi2) is determined
            # according Eq. (18)
            fi2 = fi1+1./3.*(fip1-fi)

            # apply monotonicity filter for interval before
            # check if there is "M" or "W" shape
            if     np.sign(f[-5]-f[-6]) * np.sign(f[-4]-f[-5]) == -1 \
               and np.sign(f[-4]-f[-5]) * np.sign(f[-3]-f[-4]) == -1 \
               and np.sign(f[-3]-f[-4]) * np.sign(f[-2]-f[-3]) == -1:

                # the monotonicity filter corrects the value at (fim1) by
                # substituting (fim1) with fmon, see Eq. (27), (28) and (29)
                fmon = min(3. * g[i - 2],
                           3. * g[i - 1],
                           np.sqrt(max(0, (18. / 13. * g[i - 2] - 5. / 13. * f[-7]) *
                                       (18. / 13. * g[i - 1] - 5. / 13. * f[-1]))))

                # recomputation of the sub-grid interval values while the
                # interval boundaries (fi) and (fip2) remains unchanged
                # see Eq. (18) and (19)
                f[-4] = fmon
                f[-6] = 3./2.*g[i-2]-5./12.*fmon-1./12.*f[-7]
                f[-5] = f[-6]+(fmon-f[-7])/3.
                f[-3] = 3./2.*g[i-1]-5./12.*f[-1]-1./12.*fmon
                f[-2] = f[-3]+(f[-1]-fmon)/3.

            # add next interval of interpolated (sub-)grid values
            f.append(fi1)
            f.append(fi2)
            f.append(fip1)

    # separate treatment of the final interval

    # as a requirement:
    # if there is a zero data value such that g[i]=0, then the whole
    # interval in f has to be zero to such that f[i+1]=f[i+2]=f[i+3]=0
    # according to Eq. (6)
    if g[-1] == 0.:
        # apply monotonicity filter for interval before
        # check if there is "M" or "W" shape
        if     np.sign(f[-5]-f[-6]) * np.sign(f[-4]-f[-5]) == -1 \
           and np.sign(f[-4]-f[-5]) * np.sign(f[-3]-f[-4]) == -1 \
           and np.sign(f[-3]-f[-4]) * np.sign(f[-2]-f[-3]) == -1:

            # the monotonicity filter corrects the value at (fim1) by
            # substituting (fim1) with (fmon), see Eq. (27), (28) and (29)
            fmon = min(3. * g[-3],
                       3. * g[-2],
                       np.sqrt(max(0, (18. / 13. * g[-3] - 5. / 13. * f[-7]) *
                                   (18. / 13. * g[-2] - 5. / 13. * f[-1]))))

            # recomputation of the sub-grid interval values while the
            # interval boundaries (fi) and (fip2) remains unchanged
            # see Eq. (18) and (19)
            f[-4] = fmon
            f[-6] = 3./2.*g[-3]-5./12.*fmon-1./12.*f[-7]
            f[-5] = f[-6]+(fmon-f[-7])/3.
            f[-3] = 3./2.*g[-2]-5./12.*f[-1]-1./12.*fmon
            f[-2] = f[-3]+(f[-1]-fmon)/3.

        f.extend([0., 0., 0.])

    # otherwise the sub-grid values are calculated and added to the list
    # using the persistence hypothesis as boundary condition
    else:
        # temporal save of last value in interpolated list
        # since it is the left boundary and hence the new (fi) value
        fi = f[-1]
        # since last interval in series, last value is also fip1
        fip1 = g[-1]
        # the function value at the first sub-grid point (fi1) is determined
        # according to the equal area condition with Eq. (19)
        fi1 = 3./2.*g[-1]-5./12.*fip1-1./12.*fi
        # the function value at the second sub-grid point (fi2) is determined
        # according Eq. (18)
        fi2 = fi1+dt/3.*(fip1-fi)

        # apply monotonicity filter for interval before
        # check if there is "M" or "W" shape
        if     np.sign(f[-5]-f[-6]) * np.sign(f[-4]-f[-5]) == -1 \
           and np.sign(f[-4]-f[-5]) * np.sign(f[-3]-f[-4]) == -1 \
           and np.sign(f[-3]-f[-4]) * np.sign(f[-2]-f[-3]) == -1:

            # the monotonicity filter corrects the value at (fim1) by
            # substituting (fim1) with (fmon), see Eq. (27), (28) and (29)
            fmon = min(3. * g[-3],
                       3. * g[-2],
                       np.sqrt(max(0, (18. / 13. * g[-3] - 5. / 13. * f[-7]) *
                                   (18. / 13. * g[-2] - 5. / 13. * f[-1]))))

            # recomputation of the sub-grid interval values while the
            # interval boundaries (fi) and (fip2) remains unchanged
            # see Eq. (18) and (19)
            f[-4] = fmon
            f[-6] = 3./2.*g[-3]-5./12.*fmon-1./12.*f[-7]
            f[-5] = f[-6]+(fmon-f[-7])/3.
            f[-3] = 3./2.*g[-2]-5./12.*f[-1]-1./12.*fmon
            f[-2] = f[-3]+(f[-1]-fmon)/3.

        # add next interval of interpolated (sub-)grid values
        f.append(fi1)
        f.append(fi2)
        f.append(fip1)

    return f
