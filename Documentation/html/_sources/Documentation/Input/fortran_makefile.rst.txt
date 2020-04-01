**************************************
The Fortran Makefile - ``calc_etadot``
**************************************

.. _ref-convert:

``Flex_extract``'s Fortran program will be compiled during 
the installation process to get the executable named ``calc_etadot``. 

``Flex_extract`` has a couple of ``makefiles`` prepared which can be found in the directory 
``flex_extract_vX.X/Source/Fortran``, where ``vX.X`` should be substituted with the current version number.
A list of these ``makefiles`` are shown below: 


| **Remote/Gateway mode**: 
| Files to be used as they are!
    
    | **makefile_ecgate**
    | For the use on ECMWF's server **ecgate**.

    | **makefile_cray**
    | For the use on ECMWF's server **cca/ccb**. 
    
| **Local mode**
| It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB**
 
    | **makefile_fast**
    | For the use with gfortran compiler and optimization mode.

    | **makefile_debug**
    | For the use with gfortran compiler in debugging mode.


For instructions on how to adapt the ``makefiles`` for the local application mode
please see :ref:`ref-install-local`.


   
.. toctree::
    :hidden:
    :maxdepth: 2
