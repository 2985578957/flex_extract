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
    
    | **makefile_ecgate**: For  use on the ECMWF server **ecgate**.
    | **makefile_cray**:   For  use on the ECMWF servers **cca/ccb**. 
    
| **Local mode**
| It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB** if they don't correspond to the standard paths pre-set in the makefiles.
 
    | **makefile_fast**:  For use with the gfortran compiler and optimisation mode.
    | **makefile_debug**: For use with the gfortran compiler and debugging mode. Primarily for developers.
    | **makefile_local_gfortran**: Linked to makefile_fast. Default value.

They can be found at ``flex_extract_vX.X/Source/Fortran/``, where ``vX.X`` should be substituted by the current flex_extract version number.

.. caution::   
   It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB** in these
   ``makefiles`` if other than standard paths are used.

Thus, go to the ``Fortran`` source directory and open the ``makefile`` of your 
choice, and check / modify with an editor of your choice:

.. code-block:: bash 

   cd flex_extract_vX.X/Source/Fortran
   nedit makefile_fast
 
Set the paths to the ``eccodes`` library on your local machine, if necessary.

.. caution::
   This can vary from system to system. 
   It is suggested to use a command like 

   .. code-block:: bash

      # for the ECCODES_INCLUDE_DIR path do:
      $ dpkg -L libeccodes-dev | grep eccodes.mod
      # for the ECCODES_LIB path do:
      $ dpkg -L libeccodes-dev | grep libeccodes.so
      
   to find out the path to the ``eccodes`` library.
   
Assign these paths to the parameters **ECCODES_INCLUDE_DIR**
and **ECCODES_LIB** in the makefile, and save it.

.. code-block:: bash

   # these are the paths on Debian Buster:
   ECCODES_INCLUDE_DIR=/usr/lib/x86_64-linux-gnu/fortran/gfortran-mod-15/
   ECCODES_LIB= -L/usr/lib -leccodes_f90 -leccodes -lm  
   

If you want to use another compiler than gfortran locally, you can still take ``makefile_fast``,
and adapt everything that is compiler-specific in this file.

   
.. toctree::
    :hidden:
    :maxdepth: 2
