========
Overview
========

``Flex_extract`` is an open-source software to retrieve meteorological fields from the European Centre for Medium-Range Weather Forecasts (ECMWF) Mars archive to serve as input files for the ``FLEXTRA``/``FLEXPART`` Atmospheric Transport Modelling system.
``Flex_extract`` was created explicitly for ``FLEXPART`` users who wants to use meteorological data from ECMWF to drive the ``FLEXPART`` model. 
The software retrieves the minimal number of parameters ``FLEXPART`` needs to work and provides the data in the explicity format ``FLEXPART`` understands.

``Flex_extract`` consists of 2 main parts:
    1. a Python part, where the reading of parameter settings, retrieving data from MARS and preparing the data for ``FLEXPART`` is done and 
    2. a Fortran part, where the calculation of the vertical velocity is done and if necessary the conversion from spectral to regular latitude/longitude grids.

Additionally, it has some Korn shell scripts which are used to set the environment and batch job features on ECMWF servers for the *gateway* and *remote* mode. See :doc:`Overview/app_modes` for information of application modes.   

A number of Shell scripts are wrapped around the software package for easy installation and fast job submission. 

The software depends on a number of third-party libraries which can be found in :ref:`ref-requirements`.

Some details on the tasks and program worksteps are described in :doc:`Overview/prog_flow`.


..  - directory structure (new diagramm!)
           
    - Software components - complete component structure (table or diagram)
           
       - Python package
           
           - Package diagram
           - Files and modules as table with information about unit tests
           - Api
             
       - Fortran program - calc_etadot
           
           - Package diagram
           - Api
             




    
.. toctree::
    :hidden:
    :maxdepth: 2
    
    Overview/app_modes
    Overview/prog_flow
