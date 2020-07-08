*******************
Vertical wind
*******************
        
Calculation of vertical velocity and preparation of output files
================================================================

Two methods are provided in ``flex_extract`` for the calculation of the vertical velocity for ``FLEXTRA``/``FLEXPART``: 

(i) from the horizontal wind field, 
(ii) from the MARS parameter 77, which is available for operational forecasts and analyses since September 2008 and for reanalysis datasets **ERA5** and **CERA-20C**, which contains the vertical velocity directly in the eta coordinate system of the ECMWF model.

Especially for high resolution data, use of the ``MARS`` parameter 77 is recommended,
since the computational cost (measured in ECMWF HPC units) is reduced by 90-95% at
T799. The extraction time, which depends heavily also on the performance of ``MARS``, is
generally reduced by 50% as well. The ``MARS`` parameter 77 is then multiplied by ``dp/deta`` to
give a vertical velocity in Pa/s as needed by ``FLEXPART``.

Calculation from the horizontal wind field is still required for historical case studies using
**ERA-40**, **ERA-Interim** or operational data prior to September 2008.    
    
    
Calculation of the vertical velocity from the horizontal wind using the continuity equation
===========================================================================================

The vertical velocity in the ECMWF's eta vertical coordinate system is computed by the Fortran program ``calc_etadot``, using the continuity equation and thereby ensuring mass-consistent 3D wind fields. A detailed description of ``calc_etadot`` can be found in the
documents v20_update_protocol.pdf, V30_update_protocol.pdf and
V40_update_protocol.pdf. The computational demand and accuracy of ``calc_etadot`` is highly
dependent on the specification of parameters ``GAUSS``, ``RESOL`` and ``SMOOTH``. The
following guidance can be given for choosing the right parameters:

    * For very fine output grids (0.25 degree or finer), the full resolution T799 or even T1279 of the operational model is required (``RESOL=799``, ``SMOOTH=0``). The highest available resolution (and the calculation of vertical velocity on the Gaussian grid (``GAUSS=1``) is, however, rather demanding and feasible only for resolutions up to T799. Higher resolutions are achievable on the HPC. If data retrieval at T1279  needs to be performed on *ecgate*, the computation of the vertical velocity is feasible only on the lat/lon grid (``GAUSS=0``), which also yields very good results. Please read document v20_update_protocol.pdf-v60_update_protocol.pdf to see if the errors incurred are acceptable for the planned application.
    * For lower resolution (often global) output grids, calculation of vertical velocities with lower than operational spectral resolution is recommended. For global grids the following settings appear optimal:
    
        - For 1.0 degree grids: ``GAUSS=1``, ``RESOL=255``, ``SMOOTH=179``
        - For 0.5 degree grids: ``GAUSS=1``, ``RESOL=399``, ``SMOOTH=359``
        - Calculation on the lat/lon grid is not recommended for less than the operational (T1279) resolution.    
        - If ``GAUSS`` is set to 1, only the following choices are possible for ``RESOL`` on *ecgate*: 159,255,319,399,511,799, (on the HPC also 1279; 2047 in future model versions). This choice is restricted because a reduced Gaussian grid is defined in the ECMWF EMOSLIB only for these spectral resolutions. For ``GAUSS=0``, ``RESOL`` can be any value below the operational resolution.
        - For ``SMOOTH``, any resolution lower than ``RESOL`` is possible. If no smoothing is desired, ``SMOOTH=0`` should be chosen. ``SMOOTH`` has no effect if the vertical velocity is calculated on a lat\/lon grid (``GAUSS=0``).
    * The on-demand scripts send an error message for settings where ``SMOOTH`` (if set) and ``RESOL`` are larger than 360./``GRID``/2, since in this case, the output grid cannot resolve the highest wave numbers. The scripts continue operations, however.
    * Regional grids are not cyclic in zonal directions, but global grids are. The software assumes a cyclic grid if ``RIGHT``-``LEFT`` is equal to ``GRID`` or is equal to ``GRID``-360. 
    * Finally, model and flux data as well as the vertical velocity computed are written to files ``<prefix>yymmddhh`` (the standard ``flex_extract`` output files) If the parameters ``OMEGA`` or ``OMEGADIFF`` are set, also files ``OMEGAyymmddhh`` are created, containing the pressure vertical velocity (omega) and the difference between omega from ``MARS`` and from the surface pressure tendency. ``OMEGADIFF`` should be set to zero except for debugging, since it triggers expensive calculations on the Gaussian grid.
    
    
Calculation of the vertical velocity from the pre-calculated MARS parameter 77
==============================================================================

Since November 2008, the parameter 77 (deta/dt) is stored in ``MARS`` on full model levels. ``FLEXTRA``/``FLEXPART`` in its current version requires ``deta/dt`` on model half levels, multiplied by ``dp/deta``. In ``flex_extract``, the program ``calc_etadot`` assumes that parameter 77 is available if the ``CONTROL`` parameter ``ETA`` is set to 1. 

It is recommended to use the pre-calculated parameter 77 by setting ``ETA`` to 1 whenever possible.

Setting the parameter ``ETA`` to 1 disables calculation of vertical velocity from the horizontal wind field, which saves a lot of computational time. 

.. note::
   However, the calculations on the Gaussian grid are avoided only if both ``GAUSS`` and ``ETADIFF`` are set to 0. Please set ``ETADIFF`` to 1 only if you are really need it for debugging since this is a very expensive option. In this case, ``ETAyymmddhh`` files are produced that contain the vertical velocity from horizontal winds and the difference to the pre-calculated vertical velocity.

The parameters ``RESOL``, ``GRID``, ``UPPER``, ``LOWER``, ``LEFT``, ``RIGHT`` still apply. As for calculations on the Gaussian grid, the spectral resolution parameter ``RESOL`` should be compatible with the grid resolution (see previous subsection).
    
        
.. toctree::
    :hidden:
    :maxdepth: 2
    
