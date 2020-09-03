***********************
Local mode installation
***********************

.. role:: underline
    :class: underline
    
.. toctree::
    :hidden:
    :maxdepth: 2
         
    
.. _Python3: https://www.python.org/
.. _Anaconda Python3: https://www.anaconda.com/distribution/
.. _numpy: http://www.numpy.org/
.. _ecmwf-api-client: https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home
.. _cdsapi: https://cds.climate.copernicus.eu/api-how-to
.. _genshi: https://genshi.edgewall.org/
.. _eccodes for python: https://pypi.org/project/eccodes/ 
.. _eccodes for conda: https://anaconda.org/conda-forge/python-eccodes
.. _gfortran: https://gcc.gnu.org/wiki/GFortran
.. _fftw3: http://www.fftw.org
.. _eccodes: https://software.ecmwf.int/wiki/display/ECC
.. _emoslib: https://software.ecmwf.int/wiki/display/EMOS/Emoslib
.. _member state: https://www.ecmwf.int/en/about/who-we-are/member-states 
.. _registration form: https://apps.ecmwf.int/registration/
.. _CDS API registration: https://cds.climate.copernicus.eu/user/register
.. _ECMWF ectrans site: https://confluence.ecmwf.int/display/ECAC/Unattended+file+transfer+-+ectrans
.. _ECaccess Presentation: https://confluence.ecmwf.int/download/attachments/45759146/ECaccess.pdf
.. _ECMWF instructions on gateway servers: https://confluence.ecmwf.int/display/ECAC/ECaccess+Home
.. _Computing Representative: https://www.ecmwf.int/en/about/contact-us/computing-representatives
.. _MARS access: https://confluence.ecmwf.int//display/WEBAPI/Access+MARS
.. _download section: https://www.flexpart.eu/downloads

     
.. _ref-local-mode:

.. _ref-req-local: 
 
Local mode - dependencies
=========================

The installation is the same for the access modes **member** and **public**.

The environment on your local system has to provide the following software packages
and libraries, since the preparation of the extraction and the post-processing is done on the local machine:

+------------------------------------------------+----------------+
|  Python code                                   | Fortran code   |
+------------------------------------------------+----------------+
| * `Python3`_                                   | * `gfortran`_  |
| * `numpy`_                                     | * `fftw3`_     |
| * `genshi`_                                    | * `eccodes`_   |
| * `eccodes for python`_                        | * `emoslib`_   |
| * `ecmwf-api-client`_ (everything except ERA5) |                |
| * `cdsapi`_ (just for ERA5 and member user)    |                |
+------------------------------------------------+----------------+


.. _ref-prep-local:

Preparing the local environment
===============================

The easiest way to install all required packages is to use the package management system of your Linux distribution which requires admin rights.
The installation was tested on a *Debian GNU/Linux buster* and an *Ubuntu 18.04 Bionic Beaver* system.

.. code-block:: sh

  # On a Debian or Debian-derived (e. g. Ubuntu) system,
  # you may use the following commands (or equivalent commands of your preferred package manager):
  # (if respective packages are not already available):
   apt-get install python3 (usually already available on GNU/Linux systems)
   apt-get install python3-eccodes
   apt-get install python3-genshi
   apt-get install python3-numpy
   apt-get install gfortran
   apt-get install fftw3-dev 
   apt-get install libeccodes-dev
   apt-get install libemos-dev 
  # Some of these packages will pull in further packages as dependencies. 
  # This is fine, and some are even needed by ``flex_extract''.

  # As currently the CDS and ECMWF API packages are not available as Debian packages,
  # they need to be installed outside of the Debian (Ubuntu etc.) package management system. 
  # The recommended way is:
   apt-get install pip
   pip install cdsapi 
   pip install ecmwf-api-client 
   
.. note::

    If you are using Anaconda Python, we recommend to follow the installation instructions of 
    `Anaconda Python Installation for Linux <https://docs.anaconda.com/anaconda/install/linux/>`_ 
    and then install the ``eccodes`` package from ``conda`` with:

    .. code-block:: bash

       conda install conda-forge::python-eccodes   
   
The CDS API (``cdsapi``) is required for ERA5 data and the ECMWF Web API (ecmwf-api-client) for all other public datasets.   
    
.. note:: 

    Since **public users** currently don't have access to the full *ERA5* dataset, they can skip the installation of the CDS API. 

Both user groups have to provide keys with their credentials for the Web APIs in their home directory, following these instructions:
       
ECMWF Web API:
   Go to the `MARS access`_ website and log in with your credentials. Afterwards, go to the section "Install ECMWF KEY", where the key for the ECMWF Web API should be listed. Please follow the instructions in this section under 1 (save the key in a file ``.ecmwfapirc`` in your home directory). 
     
CDS API:
   Go to `CDS API registration`_ and register there, too. Log in on the `cdsapi`_ website and follow the instructions in the section "Install the CDS API key" to save your credentials in file ``.cdsapirc``.

   
.. _ref-test-local:
   
Testing the local environment
=============================

Check the availability of the python packages by typing ``python3`` in a terminal window and run the ``import`` commands in the python shell:

.. code-block:: python
    
   # check in python3 console
   import eccodes
   import genshi
   import numpy
   import cdsapi
   import ecmwfapi
   
If there are no error messages, you succeeded in setting up the environment.


Testing the Web APIs
--------------------

You can start very simple test retrievals for both Web APIs to be sure that everything works. This is recommended to minimise the range of possible errors using ``flex_extract`` later on.


ECMWF Web API
^^^^^^^^^^^^^


+----------------------------------------------------------+----------------------------------------------------------+
|Please use this Python code snippet as a **Member user**: |Please use this Python code snippet as a **Public user**: |
+----------------------------------------------------------+----------------------------------------------------------+
|.. code-block:: python                                    |.. code-block:: python                                    |
|                                                          |                                                          |
|    from ecmwfapi import ECMWFService                     |    from ecmwfapi import ECMWFDataServer                  |
|                                                          |                                                          |
|    server = ECMWFService('mars')                         |    server = ECMWFDataServer()                            |
|                                                          |                                                          |
|    server.retrieve({                                     |    server.retrieve({                                     |
|        'stream'    : "oper",                             |        'stream'    : "enda",                             |
|        'levtype'   : "sfc",                              |        'levtype'   : "sfc",                              |
|        'param'     : "165.128/166.128/167.128",          |        'param'     : "165.128/166.128/167.128",          |
|        'dataset'   : "interim",                          |        'dataset'   : "cera20c",                          |
|        'step'      : "0",                                |        'step'      : "0",                                |
|        'grid'      : "0.75/0.75",                        |        'grid'      : "1./1.",                            |
|        'time'      : "00/06/12/18",                      |        'time'      : "00/06/12/18",                      |
|        'date'      : "2014-07-01/to/2014-07-31",         |        'date'      : "2000-07-01/to/2000-07-31",         |
|        'type'      : "an",                               |        'type'      : "an",                               |
|        'class'     : "ei",                               |        'class'     : "ep",                               |
|        'target'    : "download_erainterim_ecmwfapi.grib" |        'target'    : "download_cera20c_ecmwfapi.grib"    |
|    })                                                    |    })                                                    |
+----------------------------------------------------------+----------------------------------------------------------+

            
    
CDS API 
^^^^^^^

Extraction of ERA5 data via CDS API might take time as currently there is a high demand for ERA5 data. Therefore, as a simple test for the API just retrieve pressure-level data (even if that is NOT what we need for FLEXPART), as they are stored on disk and don't need to be retrieved from MARS (which is the time-consuming action): 

Please use the following Python code snippet to retrieve a small sample of *ERA5* pressure level data:

.. code-block:: python

    import cdsapi
    
    c = cdsapi.Client()
    
    c.retrieve("reanalysis-era5-pressure-levels",
    {
    "variable": "temperature",
    "pressure_level": "1000",
    "product_type": "reanalysis",
    "year": "2008",
    "month": "01",
    "day": "01",
    "time": "12:00",
    "format": "grib"
    },
    "download_cdsapi.grib")

    
If you know that your CDS API works, you can try to extract some data from MARS. 

.. **Member-state user**

Please use the following Python code snippet to retrieve a small *ERA5* data sample as a **member-state user**! The **Public user** do not have access to the full *ERA5* dataset!

.. code-block:: python

   import cdsapi
   
   c = cdsapi.Client()
   
   c.retrieve('reanalysis-era5-complete',
   {
       'class'   : 'ea',
       'expver'  : '1',
       'stream'  : 'oper',
       'type'    : 'fc',
       'step'    : '3/to/12/by/3',
       'param'   : '130.128',
       'levtype' : 'ml',
       'levelist': '135/to/137',
       'date'    : '2013-01-01',
       'time'    : '06/18',
       'area'    : '50/-5/40/5',
       'grid'    : '1.0/1.0', 
       'format'  : 'grib',
   }, 'download_era5_cdsapi.grib')


..  ********************** COMMENTED OUT FOR FUTURE 
    ********************** PUBLIC RETRIEVAL IS CURRENTLY NOT ACCESSIBLE 
   
    **Public user**
    Please use this piece of Python code: 

    .. code-block:: python

       import cdsapi
       
       c = cdsapi.Client()
       
       c.retrieve('reanalysis-era5-complete',
       {
           'class'   : 'ea',
           'dataset' : 'era5',
           'expver'  : '1',
           'stream'  : 'oper',
           'type'    : 'fc',
           'step'    : '3/to/12/by/3',
           'param'   : '130.128',
           'levtype' : 'ml',
           'levelist': '135/to/137',
           'date'    : '2013-01-01',
           'time'    : '06/18',
           'area'    : '50/-5/40/5',
           'grid'    : '1.0/1.0', 
           'format'  : 'grib',
       }, 'download_era5_cdsapi.grib')



.. _ref-install-local:

Local installation
==================

   
The Fortran program called ``calc_etadot`` will be compiled during the 
installation process. A suitable makefile (``makefile_local_gfortran``) for the compilation is set by default.
This may be overwritten by the ``MAKEFILE`` parameter in ``setup.sh``.

However, you may have to adapt the makefile for your environment (the current default makefile works on Debian stretch and similar GNU/Linux distributions). If you use a new name for it, you will have to insert it into ``setup.sh``
For details on the makefile and how to adapt them, see :ref:`Fortran Makefile <ref-convert>`.

 
In the root directory of ``flex_extract``, open the ``setup.sh`` script 
with an editor and adapt the installation parameters in the section labelled with 
"AVAILABLE COMMANDLINE ARGUMENTS TO SET" as shown below:


.. code-block:: bash
   :caption: 'Example settings for a local installation.'
   :name: setup.sh
   
   ...
   # -----------------------------------------------------------------
   # AVAILABLE COMMANDLINE ARGUMENTS TO SET
   #
   # THE USER HAS TO SPECIFY THESE PARAMETER
   #
   TARGET='local'
   MAKEFILE=<name_of_your_makefile>
   ECUID=None
   ECGID=None
   GATEWAY=None
   DESTINATION=None
   INSTALLDIR=None
   JOB_TEMPLATE=''
   CONTROLFILE='CONTROL_EA5'
   ...


Afterwards, type:

.. code-block:: bash

   $ ./setup.sh
   
to start the installation. You should see the following standard output. 
    
    
.. code-block:: bash

    # Output of setup.sh   
    WARNING: installdir has not been specified
    flex_extract will be installed in here by compiling the Fortran source in <path-to-flex_extract>/flex_extract_v7.1/Source/Fortran
    Install flex_extract_v7.1 software at local in directory <path-to-flex_extract>/flex_extract_v7.1

    Using makefile: makefile_local_gfortran
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./rwgrib2.f90
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./phgrreal.f90
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./grphreal.f90
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./ftrafo.f90
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./calc_etadot.f90
    gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c ./posnam.f90
    gfortran  rwgrib2.o calc_etadot.o ftrafo.o grphreal.o posnam.o phgrreal.o -o calc_etadot_fast.out  -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -lemosR64 -fopenmp
    ln -sf calc_etadot_fast.out calc_etadot

    lrwxrwxrwx. 1 <username> tmc 20 Aug 12  10:59 ./calc_etadot -> calc_etadot_fast.out

