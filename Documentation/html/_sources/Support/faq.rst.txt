################################
FAQ - Frequently asked questions
################################

.. contents::
    :local:
    
    

What can I do if I can't install the third-party libraries from distribution packages?
======================================================================================

This can be the case if the user does not have admin rights and the sysadmins would not want to provide the libraries. 
In this case, a workaround is to install the necessary libraries from source into a user directory, following these steps:

Steps to install libraries from source:
    1. `Read Emoslib installation instructions <https://software.ecmwf.int/wiki/display/EMOS/Emoslib>`_
    2. `Read ECMWF blog about gfortran <https://software.ecmwf.int/wiki/display/SUP/2015/05/11/Building+ECMWF+software+with+gfortran>`_
    3. `Install FFTW <http://www.fftw.org>`_
    4. `Install EMOSLIB <https://software.ecmwf.int/wiki/display/EMOS/Emoslib>`_ (execute ``make`` two times! One time without any options, and another time with the single-precision option.)
    5. `Install ECCODES <https://software.ecmwf.int/wiki/display/ECC>`_
    6. Register for MARS access (:ref:`ref-registration`)
    7. Install Web API's `CDS API <https://cds.climate.copernicus.eu/api-how-to>`_ and `ECMWF Web API <https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home>`_
    8. Check whether LD_LIBRARY_PATH environment variable contains the paths to all the libs
    9. Check available Python packages (e.g. ``import eccodes`` / ``import grib_api`` / ``import ecmwfapi``)
    10. Start test retrieval (:ref:`ref-test-local`)
    11. Install ``flex_extract`` (:doc:`../installation`)

.. caution::
    - use the same compiler and compiler version all the time
    - don't forget to set all Library paths in the LD_LIBRARY_PATH environment variable
    - adapt the ``flex_extract`` makefile


.. toctree::
    :hidden:
    :maxdepth: 2
