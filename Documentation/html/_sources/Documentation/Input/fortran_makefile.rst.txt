***********************************
The Fortran Makefile - ``CONVERT2``
***********************************

.. _ref-convert:

``Flex_extract``'s Fortran program will be compiled during 
the installation process to get the executable named ``CONVERT2``. 

``flex_extract`` has a couple of ``Makefiles`` prepared which can be found in the directory 
``flex_extract_vX.X/source/fortran``, where ``vX.X`` should be substituted with the current version number.
A list of these ``Makefiles`` are shown below: 


| **Remote/Gateway mode**: 
| Files to be used as they are!
    
    | **Makefile.gfortran**
    | For the use on ECMWF's server **ecgate**.

    | **Makefile.CRAY**
    | For the use on ECMWF's server **cca/ccb**. 
    
| **Local mode**
| It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB**
 
    | **Makefile.local.gfortran**
    | For the use with gfortran compiler.

    | **Makefile.local.ifort**
    | For the use with ifort compiler.


For instructions on how to adapt the ``Makefiles`` for the local application mode
please see :ref:`ref-install-local`.


   
.. toctree::
    :hidden:
    :maxdepth: 2
