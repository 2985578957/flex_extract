################################
FAQ - Frequently asked questions
################################

.. contents::
    :local:
    
    

What can I do if I can't install the third party libraries from distribution packages?
======================================================================================

This can be the case if the user does not have admin rights. 
It is possible to install the necessary libraries locally from source. 
For this case you should follow the following steps:

Installation hints:
    1. `Read Emoslib installation instructions <https://software.ecmwf.int/wiki/display/EMOS/Emoslib>`_
    2. `Read ECMWF blog about gfortran <https://software.ecmwf.int/wiki/display/SUP/2015/05/11/Building+ECMWF+software+with+gfortran>`_
    3. `Install FFTW <http://www.fftw.org>`_
    4. `Install EMOSLIB <https://software.ecmwf.int/wiki/display/EMOS/Emoslib>`_ (2 times make! one without any options and one with single precision option)
    5. `Install ECCODES <https://software.ecmwf.int/wiki/display/ECC>`_
    6. Register at Mars (:ref:`ref-registration`)
    7. Install Web API's `CDS API <https://cds.climate.copernicus.eu/api-how-to>`_ and `ECMWF Web API <https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home>`_
    8. Check LD_LIBRARY_PATH environment variable if it contains all paths to the libs
    9. Check available python packages (e.g. import eccodes / import grib_api / import ecmwfapi)
    10. Start test retrieval (:ref:`ref-test-local`)
    11. Install ``flex_extract`` (:doc:`../installation`)

.. caution::
    - use the same compiler and compiler version all the time
    - don't forget to set all Library paths in the LD_LIBRARY_PATH environment variable
    - adapt the ``flex_extract`` makefile


.. toctree::
    :hidden:
    :maxdepth: 2
