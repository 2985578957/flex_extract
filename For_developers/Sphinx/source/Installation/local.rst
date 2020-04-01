***********************
Local mode installation
***********************

.. role:: underline
    :class: underline
    
.. toctree::
    :hidden:
    :maxdepth: 2
         
    
.. _Python 3: https://docs.python.org/3/
.. _Python3: https://www.python.org/downloads/
.. _Anaconda Python3: https://www.anaconda.com/distribution/#download-section

.. _numpy: http://www.numpy.org/
.. _ecmwf-api-client: https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home
.. _cdsapi: https://cds.climate.copernicus.eu/api-how-to
.. _genshi: https://genshi.edgewall.org/
.. _eccodes for python: https://packages.debian.org/sid/python3-eccodes 
.. _eccodes for conda: https://anaconda.org/conda-forge/eccodes
.. _gfortran: https://gcc.gnu.org/wiki/GFortran
.. _fftw3: http://www.fftw.org
.. _eccodes: https://software.ecmwf.int/wiki/display/ECC
.. _emoslib: https://software.ecmwf.int/wiki/display/EMOS/Emoslib
.. _member state: https://www.ecmwf.int/en/about/who-we-are/member-states 
.. _registration form: https://apps.ecmwf.int/registration/
.. _CDS API registration: https://cds.climate.copernicus.eu/user/register
.. _ECMWF ectrans site: https://confluence.ecmwf.int/display/ECAC/Unattended+file+transfer+-+ectrans
.. _ECaccess Presentation: https://confluence.ecmwf.int/download/attachments/45759146/ECaccess.pdf
.. _ECMWF's instructions on gateway server: https://confluence.ecmwf.int/display/ECAC/ECaccess+Home
.. _Computing Representative: https://www.ecmwf.int/en/about/contact-us/computing-representatives
.. _MARS access: https://confluence.ecmwf.int//display/WEBAPI/Access+MARS

.. _download section: https://www.flexpart.eu/downloads

 
    
    
    
.. _ref-local-mode:



.. _ref-req-local: 
 
Local mode - dependencies
=========================

The installation is the same for the access modes **member** and **public**.

The environment on your local system has to provide these software packages
and libraries, since the preparation of the extraction and the post-processing is done on the local machine:

+------------------------------------------------+-----------------+
|  Python part                                   | Fortran part    |
+------------------------------------------------+-----------------+
| * `Python3`_                                   | * `gfortran`_   |
| * `numpy`_                                     | * `fftw3`_      |
| * `genshi`_                                    | * `eccodes`_    |
| * `eccodes for python`_                        | * `emoslib`_    |
| * `ecmwf-api-client`_ (everything except ERA5) |                 |
| * `cdsapi`_ (just for ERA5 and member user)    |                 |
+------------------------------------------------+-----------------+


.. _ref-prep-local:

Prepare local environment
=========================

The easiest way to install all required packages is to use the package management system of your Linux distribution  which requires admin rights.
The installation was tested on a *Debian GNU/Linux buster* and an *Ubuntu 18.04 Bionic Beaver* system.

.. code-block:: sh

  # On a Debian or Debian-derived sytem (e. g. Ubuntu) system you may use the following commands (or equivalent commands of your preferred package manager):
  # (if not already available):
   apt-get install python3 (usually already available on GNU/Linux systems)
   apt-get install python3-eccodes
   apt-get install python3-genshi
   apt-get install python3-numpy
   apt-get install gfortran
   apt-get install fftw3-dev 
   apt-get install libeccodes-dev
   apt-get install libemos-dev 
  # Some of these packages will pull in further packages as dependencies. This is fine, and some are even needed by ``flex_extract''.
  

  # As currently the CDS and ECMWF API packages are not available as Debian packages, they need to be installed outside of the Debian (Ubuntu etc.) package management system. The recommended way is:
   apt-get install pip
   pip install cdsapi 
   pip install ecmwf-api-client 
   
.. note::

    In case you would like to use Anaconda Python we recommend you follow the installation instructions of 
    `Anaconda Python Installation for Linux <https://docs.anaconda.com/anaconda/install/linux/>`_ and then install the
    ``eccodes`` package from ``conda`` with:

    .. code-block:: bash

       conda install conda-forge::python-eccodes   
   
The CDS API (cdsapi) is required for ERA5 data and the ECMWF Web API (ecmwf-api-client) for all other public datasets.   
    
.. note:: 

    Since **public users** currently don't have access to the full *ERA5* dataset they can skip the installation of the ``CDS API``. 

Both user groups have to provide keys with their credentials for the Web API's in their home directory. Therefore, follow these instructions:
       
ECMWF Web API:
   Go to `MARS access`_ website and log in with your credentials. Afterwards, on this site in section "Install ECMWF KEY" the key for the ECMWF Web API should be listed. Please follow the instructions in this section under 1 (save the key in a file `.ecmwfapirc` in your home directory). 
     
CDS API:
   Go to `CDS API registration`_ and register there too. Log in at the `cdsapi`_ website and follow the instructions at section "Install the CDS API key" to save your credentials in a `.cdsapirc` file.

   
.. _ref-test-local:
   
Test local environment
======================

Check the availability of the python packages by typing ``python3`` in a terminal window and run the ``import`` commands in the python shell. If there are no error messages, you succeeded in setting up the environment.

.. code-block:: python
    
   # check in python3 console
   import eccodes
   import genshi
   import numpy
   import cdsapi
   import ecmwfapi
   


Test the Web API's
------------------

You can start very simple test retrievals for both Web APIs to be sure that everything works. This is recommended to minimise the range of possible errors using ``flex_extract`` later on.


ECMWF Web API
^^^^^^^^^^^^^


+----------------------------------------------------------+----------------------------------------------------------+
|Please use this piece of Python code for **Member user**: |Please use this piece of Python code for **Public user**: |
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

Please use this piece of Python code to retrieve a small sample of *ERA5* pressure levels:

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

Please use this piece of Python code to retrieve a small *ERA5* data sample as a **member-state user**! The **Public user** do not have access to the full *ERA5* dataset!

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

First prepare the Fortran ``makefile`` for your environment and set it in the ``setup.sh`` script. (See section :ref:`Fortran Makefile <ref-convert>` for more information.)
``flex_extract`` comes with two ``makefiles`` prepared for the ``gfortran`` compiler. One for the normal use ``makefile_fast`` and one for debugging ``makefile_debug`` which is usually only resonable for developers.
 
They assume that ``eccodes`` and ``emoslib`` are installed as distribution packages and can be found at ``flex_extract_vX.X/Source/Fortran``, where ``vX.X`` should be substituted with the current version number.

.. caution::   
   It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB** in these
   ``makefiles`` if other than standard paths are used.

So starting from the root directory of ``flex_extract``, 
go to the ``Fortran`` source directory and open the ``makefile`` of your 
choice to modify with an editor of your choice. We use the ``nedit`` in this case.

.. code-block:: bash 

   cd flex_extract_vX.X/Source/Fortran
   nedit makefile_fast
 
Edit the paths to the ``eccodes`` library on your local machine. 


.. caution::
   This can vary from system to system. 
   It is suggested to use a command like 

   .. code-block:: bash

      # for the ECCODES_INCLUDE_DIR path do:
      $ dpkg -L libeccodes-dev | grep eccodes.mod
      # for the ECCODES_LIB path do:
      $ dpkg -L libeccodes-dev | grep libeccodes.so
      
   to find out the path to the ``eccodes`` library.
   
Substitute these paths in the ``makefile`` for parameters **ECCODES_INCLUDE_DIR**
and **ECCODES_LIB** and save it.

.. code-block:: bash

   # these are the paths on a current Debian 10 Testing system (May 2019)
   ECCODES_INCLUDE_DIR=/usr/lib/x86_64-linux-gnu/fortran/gfortran-mod-15/
   ECCODES_LIB= -L/usr/lib -leccodes_f90 -leccodes -lm  
   
    
The Fortran program called ``calc_etadot`` will be compiled during the 
installation process.Therefore the name of the ``makefile`` to be used needs to be given in  ``setup.sh``.

In the root directory of ``flex_extract``, open the ``setup.sh`` script 
and adapt the installation parameters in the section labelled with 
"AVAILABLE COMMANDLINE ARGUMENTS TO SET" like shown below.


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
   MAKEFILE='makefile_fast'
   ECUID=None
   ECGID=None
   GATEWAY=None
   DESTINATION=None
   INSTALLDIR=None
   JOB_TEMPLATE='job.template'
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

	Using makefile: makefile_fast
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./rwgrib2.f90
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./phgrreal.f90
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./grphreal.f90
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./ftrafo.f90
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./calc_etadot.f90
	gfortran   -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -I. -I/usr/local/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c	./posnam.f90
	gfortran  rwgrib2.o calc_etadot.o ftrafo.o grphreal.o posnam.o phgrreal.o -o calc_etadot_fast.out  -O3 -march=native -Bstatic -leccodes_f90 -leccodes -Bdynamic -lm -ljasper -lemosR64 -fopenmp
	ln -sf calc_etadot_fast.out calc_etadot

	lrwxrwxrwx. 1 <username> tmc 20 15. Mär 13:31 ./calc_etadot -> calc_etadot_fast.out

