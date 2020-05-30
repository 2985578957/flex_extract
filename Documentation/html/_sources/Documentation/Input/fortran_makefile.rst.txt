****************************************
The Fortran makefile for ``calc_etadot``
****************************************

.. _ref-convert:

The Fortran program ``calc_etadot`` will be compiled during 
the installation process to produce the executable called ``calc_etadot``. 

``Flex_extract`` includes several ``makefiles``  which can be found in the directory 
``flex_extract_vX.X/Source/Fortran``, where ``vX.X`` should be substituted by the current flex_extract version number.
A list of these ``makefiles`` is shown below: 


| **Remote/Gateway mode**: 
| Files to be used as they are!
    
    | **makefile_ecgate**: For  use on ECMWF's server **ecgate**.
    | **makefile_cray**:   For  use on ECMWF's server **cca/ccb**. 
    
| **Local mode**
| It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB** if they don't correspond to the standard paths pre-set in the makefiles.
 
    | **makefile_fast**:  For use with the gfortran compiler and optimisation mode.
    | **makefile_debug**: For use with the gfortran compiler and debugging mode. Primarily for developers.

If you want to use another compiler than gfortran locally, you can still take ``makefile_fast``,
and adapt everything that is compiler-specific in this file.

For instructions on how to adapt the ``makefile`` (local application mode only),
please see :ref:`ref-install-local`.

   
.. toctree::
    :hidden:
    :maxdepth: 2
