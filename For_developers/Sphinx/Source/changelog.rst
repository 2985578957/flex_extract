Changelog
=========
    
.. toctree::
    :hidden:
    :maxdepth: 2
  
.. _CDS API: https://cds.climate.copernicus.eu/api-how-to
.. _ECMWF Web API: https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home
.. _new algorithm: https://www.geosci-model-dev.net/11/2503/2018/


.. _ref-v712:

Release v7.1.2
--------------

Changes
#########
   * changed naming of template files
   * separate loading of Python3 module in remote mode is no longer necessary
   * updated module versions for ECMWF servers
   * changed names of working directories on ECMWF servers
   * select makefile automatically regarding application mode if it was not set in ``setup.sh``
   * updated online documentation
   * converted most important Fortran code documentation from German to English 
   * deactivate writing of VERTICAL.EC file by Fortran code
   * adapt and improve Fortran regression test scripts
   * remove jasper lib from Fortran makefiles
   
   
.. _ref-v711:

Release v7.1.1
--------------

Bug fixes
#########
   * corrected naming of makefiles and Fortran program executable in online documentation
   * adapted checking for ``GATEWAY`` and ``DESTINATION`` parameter 
   * fixed Fortran makefiles to use the .f90 files on ECMWF servers

    
.. _ref-v71: 
   
Release v7.1
------------
New Features
############

   * first set of UNIT tests
   * first set of regression tests   
   * structured documentation with Sphinx
   * local retrieval via `CDS API`_ for ERA 5 data
   * simplified installation process
   * disaggregation of precipitation with a `new algorithm`_
   
Changes
#######
   * upgraded to Python3
   * applied PEP8 style guide
   * use of genshi templates 
   * modularization of Python source code
   * upgrade from grib_api to ecCodes
   * completely revised/refactored Python section
   * restructured program directories
   * Fortran program name changed from ``CONVERT2`` to ``calc_etadot``

.. _ref-v704:
   
Release v7.0.4
--------------
New Features
############

    * Ensemble retrieval for ENFO and ELDA stream (ZAMG specific with extra synthesized ensembles for ELDA stream)
 
Bug fixes
#########
 
    * various problems with ERA 5 retrieval 
    * various problems with CERA-20C retrieval
    * BASETIME retrieval option
    * `CONVERT2` FORTRAN program: initialise fields to 0.
      (introduced initialization of :literal:`field` variable in the Fortran program
      with :literal:`field=0.` in file :literal:`rwGRIB2.f90` to avoid getting unreasonable large numbers.)

.. _ref-v703:
   
Release v7.0.3
--------------
New Features
############

    * output of MARS requests to an extra file (debugging and documentation)
    * CERA-20C download
    * ERA 5 download
    * public user interface with `ECMWF Web API`_
    * use of `ECMWF Web API`_ for local retrieval version
   
.. _ref-v702:
   
Release v7.0.2
--------------
New Features
############

    * Python-based version
    
Changes
#######

    * korn shell scripts substituted by Python scripts

.. _ref-v60:
    
Release v0.1 - v6.0
-------------------

    * old version which should no longer be used         
