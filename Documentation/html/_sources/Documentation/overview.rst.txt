========
Overview
========

``Flex_extract`` is an open-source software to retrieve meteorological fields from the European Centre for Medium-Range Weather Forecasts (ECMWF) MARS archive to serve as input files for the ``FLEXTRA``/``FLEXPART`` atmospheric transport modelling system.
``Flex_extract`` was created explicitly for ``FLEXPART`` users who want to use meteorological data from ECMWF to drive the ``FLEXPART`` model. 
The software retrieves the minimum set of parameters needed by ``FLEXPART`` to work, and provides the data in the specific format required by ``FLEXPART``.

``Flex_extract`` consists of two main parts:
    1. a Python part which reads the parameter settings, retrieves the data from MARS, and prepares them for ``FLEXPART``, and 
    2. a Fortran part which calculates the vertical velocity and, if necessary, converts variables from the spectral representation to regular latitude/longitude grids.

In addition, there are some Korn shell scripts to set the environment and batch job features on ECMWF servers for the *gateway* and *remote* mode. See :doc:`Overview/app_modes` for information of application modes.   

A number of Shell scripts are wrapped around the software package for easy installation and fast job submission. 

The software depends on some third-party libraries as listed in :ref:`ref-requirements`.

Details of the tasks and program work steps are described in :doc:`Overview/prog_flow`.


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
