***********
Output Data
***********

The output data of ``flex_extract`` are separated mainly into temporary files and the final ``FLEXPART`` input files:

+-----------------------------------------------+----------------------------------------------+   
|   ``FLEXPART`` input files                    |  Temporary files (saved in debug mode)       | 
+-----------------------------------------------+----------------------------------------------+
| - Standard output filenames                   | - MARS request file (opt)                    | 
| - Output for pure forecast                    | - flux files                                 | 
| - Output for ensemble members                 | - VERTICAL.EC                                |
| - Output for new precip. disaggregation       | - index file                                 | 
|                                               | - fort files                                 | 
|                                               | - MARS grib files                            | 
+-----------------------------------------------+----------------------------------------------+ 



``FLEXPART`` input files
========================

The final output files of ``flex_extract`` are also the meteorological ``FLEXPART`` input files.
The naming of these files depend on the kind of data extracted by ``flex_extract``. 

Standard output files
---------------------
 
In general, there is a file for each time step with the filename format:

.. code-block:: bash

    <prefix>YYMMDDHH
    
The ``prefix`` is by default defined as ``EN`` and can be re-defined in the ``CONTROL`` file.
Each file contains all meteorological fields needed by ``FLEXPART`` for all selected model levels for a specific time step. 

Here is an example output which lists the meteorological fields in a single file called ``CE00010800`` where we extracted only the lowest model level for demonstration reasons:

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


Output files for pure forecast
------------------------------

``Flex_extract`` can retrieve forecasts which can be longer than 23 hours. To avoid collisions of time steps for forecasts of more than one day a new scheme for filenames in pure forecast mode is introduced:

.. code-block:: bash

    <prefix>YYMMDD.HH.<FORECAST_STEP>

The ``<prefix>`` is, as in the standard output, by default ``EN`` and can be re-defined in the ``CONTROL`` file. ``YYMMDD`` is the date format and ``HH`` the forecast time which is the starting time for the forecasts. The ``FORECAST_STEP`` is a 3 digit number which represents the forecast step in hours. 
    

Output files for ensemble predictions
-------------------------------------

Ensembles can be retrieved and are addressed by the grib message parameter ``number``. The ensembles are saved per file and standard filenames are supplemented by the letter ``N`` and the ensemble member number in a 3 digit format.

.. code-block:: bash

    <prefix>YYMMDDHH.N<ENSEMBLE_MEMBER>


Additional fields with new precipitation disaggregation
-------------------------------------------------------

The new disaggregation method for precipitation fields produces two additional precipitation fields for each time step and precipitation type. They serve as sub-grid points in the original time interval. For details of the method see :doc:`disagg` ??????????????????.
The two additional fields are marked with the ``step`` parameter in the Grib messages and are set to "1" and "2" for sub-grid point 1 and 2 respectively.
The output filenames do not change in this case.  
Below is an example list of precipitation fields in an output file generated with the new disaggregation method:

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

``Flex_extract`` works with a number of temporary data files which are usually deleted after a successful data extraction. They are only stored if the ``DEBUG`` mode is switched on (see :doc:`Input/control_params`. 

MARS grib files
---------------

``Flex_extract`` retrieves all meteorological fields from MARS and stores them in files ending with ``.grb``.
Since the request times and data transfer of MARS access are limited and ECMWF asks for efficiency in requesting data from MARS, ``flex_extract`` splits the overall data request in several smaller requests. Each request is stored in an extra ``.grb`` file and the file names are put together by several pieces of information:

    .. code-block:: bash
    
       <field_type><grid_type><temporal_property><level_type>.<date>.<ppid>.<pid>.grb

Description:
       
Field type: 
    ``AN`` - Analysis, ``FC`` - Forecast, ``4V`` - 4d variational analysis, ``CV`` - Validation forecast, ``CF`` - Control forecast, ``PF`` - Perturbed forecast
Grid type: 
   ``SH`` - Spherical Harmonics, ``GG`` - Gaussian Grid, ``OG`` - Output Grid (typically lat/lon), ``_OROLSM`` - Orography parameter
Temporal property:
    ``__`` - instantaneous fields, ``_acc`` - accumulated fields
Level type: 
    ``ML`` - Model Level, ``SL`` - Surface Level
ppid:
    The process number of the parent process of submitted script.
pid:
    The process number of the submitted script.

The process ids should avoid mixing of fields if several ``flex_extract`` jobs are performed in parallel (which is, however, not recommended). The date format is YYYYMMDDHH.

Example ``.grb`` files for a day of CERA-20C data:

    .. code-block:: bash

        ANOG__ML.20000908.71851.71852.grb  
        FCOG_acc_SL.20000907.71851.71852.grb
        ANOG__SL.20000908.71851.71852.grb  
        OG_OROLSM__SL.20000908.71851.71852.grb
        ANSH__SL.20000908.71851.71852.grb


MARS request file 
-----------------

This file is a ``csv`` file called ``mars_requests.csv`` with a list of the actual settings of MARS request parameters (one request per line) in a flex_extract job. It is used for documenting the data which were retrieved and for testing reasons.

Each request consist of the following parameters, whose meaning mainly can be taken from :doc:`Input/control_params` or :doc:`Input/run`: 
request_number, accuracy, area, dataset, date, expver, gaussian, grid, levelist, levtype, marsclass, number, param, repres, resol, step, stream, target, time, type
  
Example output of a one day retrieval of CERA-20c data: 

.. code-block:: bash

    request_number, accuracy, area, dataset, date, expver, gaussian, grid, levelist, levtype, marsclass, number, param, repres, resol, step, stream, target, time, type
    1, 24, 40.0/-5.0/30.0/5.0, None, 20000107/to/20000109, 1, , 1.0/1.0, 1, SFC, EP, 000, 142.128/143.128/146.128/180.128/181.128/176.128, , 159, 3/to/24/by/3, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/FCOG_acc_SL.20000107.23903.23904.grb, 18, FC
    1, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , 1.0/1.0, 85/to/91, ML, EP, 000, 130.128/133.128/131.128/132.128/077.128/246.128/247.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANOG__ML.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN
    2, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , OFF, 1, ML, EP, 000, 152.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANSH__SL.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN
    3, 24, 40.0/-5.0/30.0/5.0, None, 20000108, 1, , 1.0/1.0, 1, SFC, EP, 000, 160.128/027.128/028.128/244.128, , 159, 000, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/OG_OROLSM__SL.20000108.23903.23904.grb, 00, AN
    4, 24, 40.0/-5.0/30.0/5.0, None, 20000108/to/20000108, 1, , 1.0/1.0, 1, SFC, EP, 000, 141.128/151.128/164.128/165.128/166.128/167.128/168.128/129.128/172.128/027.128/028.128/186.128/187.128/188.128/235.128/139.128/039.128/173.128, , 159, 00, ENDA, /mnt/nas/Anne/Interpolation/flexextract/flex_extract_v7.1/run/./workspace/CERA_testgrid_local_cds/ANOG__SL.20000108.23903.23904.grb, 00/03/06/09/12/15/18/21, AN


VERTICAL.EC
-----------

The vertical discretization of model levels. This file contains the ``A`` and ``B`` parameters to calculate the model level height in meters.


Index file
----------

This file is usually called ``date_time_stepRange.idx``. It contains indices pointing to specific grib messages from one or more grib files. The messages are selected with a composition of grib message keywords. 


flux files
----------

The flux files contain the de-accumulated and dis-aggregated flux fields of large scale and convective precipitation, eastward turbulent surface stress, northward turbulent surface stress, surface sensible heat flux and the surface net solar radiation. 

.. code-block:: bash

    flux<date>[.N<xxx>][.<xxx>]

The date format is YYYYMMDDHH. The optional block ``[.N<xxx>]`` marks the ensemble forecast number, where ``<xxx>`` is the ensemble member number. The optional block ``[.<xxx>]`` marks a pure forecast with ``<xxx>`` being the forecast step.

.. note::

    In the case of the new dis-aggregation method for precipitation, two new sub-intervals are added in between each time interval. They are identified by the forecast step parameter which is ``0`` for the original time interval and ``1`` or ``2`` for the two new intervals respectively. 

    
fort files
----------

There are a number of input files for the ``CONVERT2`` Fortran program named

.. code-block:: bash

    fort.xx
    
where ``xx`` is the number which defines the meteorological fields stored in these files. 
They are generated by the Python part of ``flex_extract`` by just splitting the meteorological fields for a unique time stamp from the ``*.grb`` files into the ``fort`` files. 
The following table defines the numbers with their corresponding content.   

.. csv-table:: Content of fort - files
    :header: "Number", "Content"
    :widths: 5, 20
 
    "10", "U and V wind components" 
    "11", "temperature" 
    "12", "logarithm of surface pressure" 
    "13", "divergence (optional)" 
    "16", "surface fields"
    "17", "specific humidity"
    "18", "surface specific humidity (reduced gaussian)"
    "19", "vertical velocity (pressure) (optional)" 
    "21", "eta-coordinate vertical velocity (optional)" 
    "22", "total cloud water content (optional)"

Some of the fields are solely retrieved with specific settings, e.g. the eta-coordinate vertical velocity is not available in ERA-Interim datasets and the total cloud water content is an optional field for ``FLEXPART v10`` and newer. Please see section ????????? for more information. 

The ``CONVERT2`` program saves its results in file ``fort.15`` which typically contains:

.. csv-table:: Output file of the Fortran program ``CONVERT2``
    :header: "Number", "Content"
    :widths: 5, 20
 
    "15", "U and V wind components, eta-coordinate vertical velocity, temperature, surface pressure, specific humidity " 
    
More details about the content of ``CONVERT2`` can be found in :doc:`vertco`.    
    
.. note::
 
    The ``fort.4`` file is the namelist file to drive the Fortran program ``CONVERT2``. It is therefore also an input file and is described in ???????????????
    
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
    