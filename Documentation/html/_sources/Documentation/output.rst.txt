***********
Output data
***********

The output data of ``flex_extract`` can be divided into the final ``FLEXPART`` input files and  temporary files:

+-----------------------------------------------+----------------------------------------------+   
|   ``FLEXPART`` input files                    |  Temporary files (saved in debug mode)       | 
+-----------------------------------------------+----------------------------------------------+
| - Standard output file names                  | - MARS request file (optional)               | 
| - Output for pure forecast                    | - flux files                                 | 
| - Output for ensemble members                 | - VERTICAL.EC                                |
| - Output for new precip. disaggregation       | - index file                                 | 
|                                               | - fort files                                 | 
|                                               | - MARS grib files                            | 
+-----------------------------------------------+----------------------------------------------+ 



``FLEXPART`` input files
========================

The final output files of ``flex_extract`` are the meteorological input files for ``FLEXPART``.
The naming convention for these files depends on the kind of data extracted by ``flex_extract``. 

Standard output files
---------------------
 
In general, there is one file for each time named:

.. code-block:: bash

    <prefix>YYMMDDHH
    
where YY are the last two digits of the year, MM is the month, DD the day, and HH the hour (UTC). <prefix> is by default defined as EN, and can be re-defined in the ``CONTROL`` file.
Each file contains all meteorological fields at all levels as needed by ``FLEXPART``, valid for the time indicated in the file name. 

Here is an example output which lists the meteorological fields in a single file called ``CE00010800`` (where we extracted only the lowest model level for demonstration purposes):

.. code-block:: bash

        $ grib_ls CE00010800
        
        edition      centre       date         dataType     gridType     stepRange    typeOfLevel  level        shortName    packingType
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           u            grid_simple
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           v            grid_simple
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           etadot       grid_simple
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           t            grid_simple
        2            ecmf         20000108     an           regular_ll   0            surface      1            sp           grid_simple
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           q            grid_simple
        2            ecmf         20000108     an           regular_ll   0            hybrid       91           qc           grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            sshf         grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            ewss         grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            nsss         grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            ssr          grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            lsp          grid_simple
        1            ecmf         20000108     fc           regular_ll   0            surface      0            cp           grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            sd           grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            msl          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            tcc          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            10u          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            10v          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            2t           grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            2d           grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            z            grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            lsm          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            cvl          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            cvh          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            lcc          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            mcc          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            hcc          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            skt          grid_simple
        1            ecmf         20000108     an           regular_ll   0            depthBelowLandLayer  0            stl1         grid_simple
        1            ecmf         20000108     an           regular_ll   0            depthBelowLandLayer  0            swvl1        grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            sr           grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            sdor         grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            cvl          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            cvh          grid_simple
        1            ecmf         20000108     an           regular_ll   0            surface      0            fsr          grid_simple
        35 of 35 messages in CE00010800


Output files for long forecast
------------------------------

``Flex_extract`` is able to retrieve forecasts with a lead time of more than 23 hours. In order to avoid collisions of time steps names, a new scheme for filenames in long forecast mode is introduced:

.. code-block:: bash

    <prefix>YYMMDD.HH.<FORECAST_STEP>

The ``<prefix>`` is, as in the standard output, by default ``EN`` and can be re-defined in the ``CONTROL`` file. ``YYMMDD`` is the date format and ``HH`` the forecast time which is the starting time for the forecasts. The ``FORECAST_STEP`` is a 3-digit number which represents the forecast step in hours. 
    

Output files for ensemble predictions
-------------------------------------

``Flex_extract`` is able to retrieve ensembles data; they are labelled by the grib message parameter ``number``. Each ensemble member is saved in a separate file, and standard filenames are supplemented by the letter ``N`` and the ensemble member number in a 3-digit format.

.. code-block:: bash

    <prefix>YYMMDDHH.N<ENSEMBLE_MEMBER>


Additional fields with new precipitation disaggregation
-------------------------------------------------------

The new disaggregation method for precipitation fields produces two additional precipitation fields for each time step and precipitation type (large-scale and convective). They serve as sub-grid points in the original time interval. For details of the method see :doc:`disagg`.
The two additional fields are addressed using the ``step`` parameter in the GRIB messages, which
is set to "1" or "2", for sub-grid points 1 and 2, respectively.
The output file names are not altered.  
An example of the list of precipitation fields in an output file generated with the new disaggregation method is found below:

.. code-block:: bash 

    $ grib_ls 

    edition      centre       date         dataType     gridType     stepRange    typeOfLevel  level        shortName    packingType
    1            ecmf         20000108     fc           regular_ll   0            surface      0            lsp          grid_simple
    1            ecmf         20000108     fc           regular_ll   1            surface      0            lsp          grid_simple
    1            ecmf         20000108     fc           regular_ll   2            surface      0            lsp          grid_simple
    1            ecmf         20000108     fc           regular_ll   0            surface      0            cp           grid_simple
    1            ecmf         20000108     fc           regular_ll   1            surface      0            cp           grid_simple
    1            ecmf         20000108     fc           regular_ll   2            surface      0            cp           grid_simple




Temporary files
===============

``Flex_extract`` creates a number of temporary data files which are usually deleted at the end of a successful run. They are preserved only if the ``DEBUG`` mode is switched on (see :doc:`Input/control_params`). 

MARS grib files
---------------

``Flex_extract`` retrieves all meteorological fields from MARS and stores them in files ending with ``.grb``.
Since there are limits implemented by ECMWF for the time per request and data transfer from MARS, 
and as ECMWF asks for efficient MARS retrievals, ``flex_extract`` splits the overall data request 
into several smaller requests. Each request is stored in its own ``.grb`` file, and the file 
names are composed of several pieces of information:

    .. code-block:: bash
    
       <field_type><grid_type><temporal_property><level_type>.<date>.<ppid>.<pid>.grb

Description:
       
Field type: 
    ``AN`` - Analysis, ``FC`` - Forecast, ``4V`` - 4D variational analysis, ``CV`` - Validation forecast, ``CF`` - Control forecast, ``PF`` - Perturbed forecast
Grid type: 
   ``SH`` - Spherical Harmonics, ``GG`` - Gaussian Grid, ``OG`` - Output Grid (typically lat / lon), ``_OROLSM`` - Orography parameter
Temporal property:
    ``__`` - instantaneous fields, ``_acc`` - accumulated fields
Level type: 
    ``ML`` - model level, ``SL`` - surface level
ppid:
    The process number of the parent process of the script submitted.
pid:
    The process number of the script submitted.


Example ``.grb`` files for one day of CERA-20C data:

    .. code-block:: bash

        ANOG__ML.20000908.71851.71852.grb  
        FCOG_acc_SL.20000907.71851.71852.grb
        ANOG__SL.20000908.71851.71852.grb  
        OG_OROLSM__SL.20000908.71851.71852.grb
        ANSH__SL.20000908.71851.71852.grb


MARS request file 
-----------------

This file is a ``csv`` file called ``mars_requests.csv`` listing the actual settings of the MARS 
request (one request per line) in a flex_extract job. 
It is used for documenting which data were retrieved, and for testing.

Each request consists of the following parameters, whose meaning mostly can be taken from :doc:`Input/control_params` or :doc:`Input/run`: 
request_number, accuracy, area, dataset, date, expver, gaussian, grid, levelist, levtype, marsclass, number, param, repres, resol, step, stream, target, time, type
  
Example output of a one-day retrieval of CERA-20C data: 

.. code-block:: bash

    request_number, accuracy, area, dataset, date, expver, gaussian, grid, levelist, levtype, marsclass, number, param, repres, resol, step, stream, target, time, type
    1, 24, 40.0/-5.0/30.0/5.0, None, 20000107/to/20000109, 1, , 1.0/1.0, 1, SFC, EP, 000, 142.128/143.128/146.128/180.128/181.128/176.128, , 159, 3/to/24/by/3, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/FCOG_acc_SL.20000107.23903.23904.grb, 18, FC
    1, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , 1.0/1.0, 85/to/91, ML, EP, 000, 130.128/133.128/131.128/132.128/077.128/246.128/247.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANOG__ML.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN
    2, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , OFF, 1, ML, EP, 000, 152.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANSH__SL.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN
    3, 24, 40.0/-5.0/30.0/5.0, None, 20000108, 1, , 1.0/1.0, 1, SFC, EP, 000, 160.128/027.128/028.128/244.128, , 159, 000, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/OG_OROLSM__SL.20000108.23903.23904.grb, 00, AN
    4, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , 1.0/1.0, 1, SFC, EP, 000, 141.128/151.128/164.128/165.128/166.128/167.128/168.128/129.128/172.128/027.128/028.128/186.128/187.128/188.128/235.128/139.128/039.128/173.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANOG__SL.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN



Index file
----------

This file is called ``date_time_stepRange.idx``. It contains indices pointing to specific grib messages from one or more grib files. The messages are selected with a composition of grib message keywords. 


Flux files
----------

The flux files contain the de-accumulated and dis-aggregated flux fields of large-scale and convective precipitation, east- and northward turbulent surface stresses, the surface sensible heat flux, and the surface net solar radiation. 

.. code-block:: bash

    flux<date>[.N<xxx>][.<xxx>]

The date format is YYYYMMDDHH as explained before. The optional block ``[.N<xxx>]`` is used for the ensemble forecast date, where ``<xxx>`` is the ensemble member number. The optional block ``[.<xxx>]`` marks a pure forecast with ``<xxx>`` being the forecast step.

.. note::

    In the case of the new dis-aggregation method for precipitation, two new sub-intervals are added in between each time interval. They are identified by the forecast step parameter which is ``0`` for the original time interval, and ``1`` or ``2``,  respectively, for the two new intervals. 

    
fort files
----------

There are a number of input files for the ``calc_etadot`` Fortran program named

.. code-block:: bash

    fort.xx
    
where ``xx`` is a number which defines the meteorological fields stored in these files. 
They are generated by the Python code in ``flex_extract`` by splitting the meteorological fields for a unique time stamp from the ``*.grb`` files, storing them under the names ``fort.<XX>`` where <XX> represents some number. 
The following table defines the numbers and the corresponding content:   

.. csv-table:: Content of fort - files
    :header: "Number", "Content"
    :widths: 5, 20
 
    "10", "U and V wind components" 
    "11", "temperature" 
    "12", "logarithm of surface pressure" 
    "13", "divergence (optional)" 
    "16", "surface fields"
    "17", "specific humidity"
    "18", "surface specific humidity (reduced Gaussian grid)"
    "19", "omega (vertical velocity in pressure coordinates) (optional)" 
    "21", "eta-coordinate vertical velocity (optional)" 
    "22", "total cloud-water content (optional)"

Some of the fields are solely retrieved with specific settings, e. g., the eta-coordinate vertical velocity is not available in ERA-Interim datasets, and the total cloud-water content is an optional field which is useful for ``FLEXPART v10`` and newer. 

The ``calc_etadot`` program saves its results in file ``fort.15`` which typically contains:

.. csv-table:: Output file of the Fortran program ``calc_etadot``
    :header: "Number", "Content"
    :widths: 5, 20
 
    "15", "U and V wind components, eta-coordinate vertical velocity, temperature, surface pressure, specific humidity " 
    
More details about the content of ``calc_etadot`` can be found in :doc:`vertco`.    
    
.. note::
 
    The ``fort.4`` file is the namelist file to control the Fortran program ``calc_etadot``. It is therefore also an input file.
    
    Example of a namelist:
    
    .. code-block:: bash
    
        &NAMGEN
          maxl = 11,
          maxb = 11,
          mlevel = 91,
          mlevelist = "85/to/91",
          mnauf = 159,
          metapar = 77,
          rlo0 = -5.0,
          rlo1 = 5.0,
          rla0 = 30.0,
          rla1 = 40.0,
          momega = 0,
          momegadiff = 0,
          mgauss = 0,
          msmooth = 0,
          meta = 1,
          metadiff = 0,
          mdpdeta = 1
        /
        
        
.. toctree::
    :hidden:
    :maxdepth: 2
    
