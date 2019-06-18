**********************************
The Fortran Program - ``CONVERT2``
**********************************

.. _ref-convert:

One of ``flex_extract``'s components is a Fortran program called ``CONVERT2``.
This will be compiled during the installation process to get an executable. ``flex_extract`` 
has a couple of makefiles prepared which are listed in the following. 


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

They can be found in the path ``flex_extract_vX.X/source/fortran``, where
``vX.X`` should be substituted with the current version number.

So starting from the root directory of ``flex_extract``, 
go to the ``Fortran`` source directory and open the ``Makefile`` of your 
choice to modify with an editor of your choice. We use the ``nedit`` in this case.
So far, we tested ``flex_extract`` with a ``gfortran`` and an ``ifort`` compiler.  

.. code-block:: bash 

   $ cd flex_extract_vX.X/source/fortran
   $ nedit Makefile.local.gfortran


Edit the pathes to the ``eccodes`` library on your local machine. 

.. caution::
   This can vary from system to system. 
   It is suggested to use a command like 

   .. code-block:: bash

      # for the ECCODES_INCLUDE_DIR path do:
      $ dpkg -L libeccodes-dev | grep eccodes.mod
      # for the ECCODES_LIB path do:
      $ dpkg -L libeccodes-dev | grep libeccodes.so
      
   to find out the path to the ``eccodes`` library.
   
Substitute these paths in the ``Makefile`` for parameters **ECCODES_INCLUDE_DIR**
and **ECCODES_LIB** and save it.

.. code-block:: bash

   # these are the paths on a current Debian Testing system (May 2019)
   ECCODES_INCLUDE_DIR=/usr/lib/x86_64-linux-gnu/fortran/gfortran-mod-15/
   ECCODES_LIB= -L/usr/lib -leccodes_f90 -leccodes -lm  
   
   
.. toctree::
    :hidden:
    :maxdepth: 2
