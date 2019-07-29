************
Installation
************

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



``flex_extract`` is a software package which contains a mix of Python and Shell scripts as well as a Fortran program. These components rely on a couple of third party libraries which need to be prepared first before starting the installation process. For now, the software is only tested for a Linux/Unix environment. Feel free to try it out on other platforms.

Start with the decision of which `user group <Ecmwf/access>`_ you belong to and follow the instructions at :ref:`ref-registration` to get an account at ECMWF. Considering your user group and the method of applying ``flex_extract`` there appear to be 4 application modes:  

- Remote (for member state users only) :ref:`[installation]<ref-remote-mode>`
- Gateway (for member state users only) :ref:`[installation]<ref-gateway-mode>`
- Local member :ref:`[installation]<ref-local-mode>`
- Local public :ref:`[installation]<ref-local-mode>`

More information can be found in :doc:`Documentation/Overview/app_modes`.

.. note::

   If you encounter any problems in the installation process, you can ask for :doc:`support`.





.. _ref-registration:

Registration at ECMWF
=====================

Decide which user group you belong to and follow the instructions for registration:

**Member state user**: 
    To get a member-state user account, users have to be a resident of a `member state`_. In that case, you can contact your `Computing Representative`_ for granting access. If you would like to use the local application mode to retrieve **ERA5** data you'd have to register at the `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/user/register>`_ also.

**Public user**: 
    To be able to download public datasets with ``flex_extract`` such as **ERA-Interim** and **CERA-20C** (**ERA5** is not supported via ECMWF Web API anymore), the public user has to create an account at ECMWF. 
    Use the registration at the ECMWF website by filling out this `registration form`. 
    
    .. note::

        In the future retrievement of *ERA5* will be possible via the CDS API for public users also. Then a registration at the `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/user/register>`_ is needed in addition.
    
    
    
    
    
    
.. _ref-licence:
    
Agree on licences for public datasets
=====================================

Each public dataset which is intended to be downloaded by ``flex_extract`` has its own licence which has to be accepted, regardless of the user group. 

For the *ERA-Interim* and *CERA-20C* datasets this can be done at the ECMWF website `Available ECMWF Public Datasets <https://confluence.ecmwf.int/display/WEBAPI/Available+ECMWF+Public+Datasets>`_. Log in and follow the licence links on the right side for each dataset and accept it.
    
For the *ERA5* dataset this has to be done at the `Climate Data Store (CDS) website <https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset>`_. Log in with your credentials and then select on the left panel the product type "Reanalysis" for finding *ERA5* datasets. Then follow the link of a title with *ERA5* (anyone) to the full dataset record, click on tab "Download data" and scroll down. There is a section "Terms of use" where you have to click the :underline:`Accept terms` button.    

   




.. _ref-download:

Download ``flex_extract``
=========================

There are 2 options to download ``flex_extract``:

tar ball
    You can download the latest prepared release tar ball from the `download section`_ 
    of our ``FLEXPART`` community website and then untar the file. Substitute
    the **<ID>** in the ``wget`` command with the ID-number of the ``flex_extract`` 
    release tar ball in the list of downloads at the community website. 
    
    
    .. code-block:: bash
       
       wget https://www.flexpart.eu/downloads/<ID>
       tar -xvf <flex_extract_vX.X.tar>

git repo    
    Or you can clone the current release version from our git repository master branch.

    .. code-block:: bash

       $ git clone https://www.flexpart.eu/gitmob/flexpart





.. _ref-requirements: 
 
Environment requirements
========================

This is a list of the general environment requirements for ``flex_extract``.
What is required exactly for each application mode will be described in the specifc installation section. 

    
To run the python part of ``flex_extract`` a `Python 3`_ environment is needed.
We tested ``flex_extract`` with a normal Linux Python package distribution and Anaconda Python. 
Except for `Python3`_ all are python packages which can be installed via ``pip``.

* `Python3`_ or `Anaconda Python3`_
* `numpy`_
* `ecmwf-api-client`_ (Web Interface to ECMWF servers for datasets except ERA5)
* `cdsapi`_ (Web Interface to `C3S <https://climate.copernicus.eu/>`_ servers for ERA5)
* `genshi`_
* `eccodes for python`_  
 
For the Fortran part of ``flex_extract`` we need the following distribution packages: 
 
* `gfortran`_
* `fftw3`_
* `eccodes`_
* `emoslib`_






.. _ref-install-fe:

Installation of ``flex_extract``
================================

The actual installation of ``flex_extract`` will be done by executing a `Shell` script called ``setup.sh``.
It defines some parameters and calls a Python script by giving the parameters as command line arguments.
More information on the script and its parameters can be found at :doc:`Documentation/Input/setup`. 

For each application mode installation section we describe the requirements for the explicit 
environment and how it is installed, test if it works and how the actual ``flex_extract``
installation has to be done. At the users local side not all software has to be present for ``flex_extract``.






.. _ref-remote-mode: 

Remote mode
-----------

.. _ref-req-remote: 
 
Remote environment requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The environment for ``flex_extract`` on ECMWF servers has to provide these 
software packages and libraries:
    
+---------------------------+-----------------+
|  Python part              | Fortran part    |
+---------------------------+-----------------+
| * `Python3`_              | * `gfortran`_   |
| * `numpy`_                | * `fftw3`_      |
| * `genshi`_               | * `eccodes`_    |
| * `eccodes for python`_   | * `emoslib`_    |
+---------------------------+-----------------+


.. _ref-prep-remote:

Prepare remote environment
^^^^^^^^^^^^^^^^^^^^^^^^^^
 
The environment on the ECMWF server (such as *ecgate* or *cca*) is already 
prepared. ECMWF server provide all libraries via a module system which is 
going to be selected by ``flex_extract`` automatically.


.. _ref-install-remote:

Remote installation
^^^^^^^^^^^^^^^^^^^

First, log in on one of the ECMWF Linux server, such as *ecgate* or *cca/ccb*. 
Substitute *<ecuid>* with your ECMWF user name:

.. code-block:: bash
   
   ssh -X <ecuid>@ecaccess.ecmwf.int

This will lead to the following output on the command line, asking for your 
password:
   
.. code-block:: bash

   Authorized access only.

   ***************************************************************
      For further information, read the ECaccess documentation at:

      https://software.ecmwf.int/wiki/display/ECAC/ECaccess+Home

      You can also use ECaccess to load & download files from your
      EChome, ECscratch or ECfs directories using the ECaccess FTP
      server:

      ftp://uid@ecaccess.ecmwf.int/

      Please note you must use your UID and ActivID code to login!
   ***************************************************************

   <ecuid>@131.130.157.5's password: ***
   Select hostname (ecgate, cca, ccb) [ecgate]: ecgate

   [<ecuid>@ecgb11 ~]$ 
   
   
Then, copy the ``flex_extract`` tar ball (from section :ref:`ref-download`) 
to the ``$HOME`` directory of the ECMWF Linux server via ``scp``.
Substitute the *<localuser>* and *<server.edu>* placeholders with your credentials. 
Untar the file and change into the ``flex_extract`` root directory. 

.. code-block:: bash

   scp <localuser>@<server.edu>:/path/to/tarfile/flex_extract_vX.X.tar.gz  $HOME/
   cd $HOME
   tar xvf flex_extract_vX.X.tar.gz
   cd flex_extract_vX.X
   

On these ECMWF servers, it is not necessary to prepare the environment or the 
``Makefile`` for the Fortran program (``CONVERT2``) as described above. 
All third party libraries are available from a module system. The ``Makefile``
is optimized for ECMWF servers and the compilation 
script ``compilejob.ksh``, which will be submitted by ``flex_extract`` to the 
batch job queue at ECMWF, does load all relevant modules from the ECMWF's module system. 

So there is just the need to execute the ``setup.sh`` script from the 
``flex_extract`` root directory for installation. 
Before executing it, it is necessary to adapt some parameters from ``setup.sh``
described in :doc:`Documentation/Input/setup`. 

Open ``setup.sh`` with your editor and adapt the values:  

+----------------------------------------------+----------------------------------------------+   
|   Take this for target = **ectrans**         |  Take this for target = **cca**              | 
+----------------------------------------------+----------------------------------------------+
| .. code-block:: bash                         | .. code-block:: bash                         | 
|                                              |                                              | 
|   ...                                        |   ...                                        |   
|   # -----------------------------------------|   # -----------------------------------------|
|   # AVAILABLE COMMANDLINE ARGUMENTS TO SET   |   # AVAILABLE COMMANDLINE ARGUMENTS TO SET   |
|   #                                          |   #                                          |  
|   # THE USER HAS TO SPECIFY THESE PARAMETER  |   # THE USER HAS TO SPECIFY THESE PARAMETER  | 
|   #                                          |   #                                          |
|   TARGET='ecgate'                            |   TARGET='cca'                               |
|   MAKEFILE='Makefile.gfortran'               |   MAKEFILE='Makefile.CRAY'                   |  
|   ECUID='uid'                                |   ECUID='uid'                                |  
|   ECGID='gid'                                |   ECGID='gid'                                |
|   GATEWAY=None                               |   GATEWAY=None                               |
|   DESTINATION=None                           |   DESTINATION=None                           | 
|   INSTALLDIR=None                            |   INSTALLDIR=''                              | 
|   JOB_TEMPLATE='job.template'                |   JOB_TEMPLATE='job.template'                |
|   CONTROLFILE='CONTROL_EA5'                  |   CONTROLFILE='CONTROL_EA5'                  | 
|   ...                                        |   ...                                        |   
+----------------------------------------------+----------------------------------------------+

:underline:`Please substitute the values of ECUID and ECGID
with your own credentials and settings.`

.. note::

   If a local gateway server is available the transfer of files could be done
   via the ``ECaccess`` commands. Therefore a valid *GATEWAY* and *DESTINATION*
   have to be present and should be set in the ``setup.sh`` file. 


Afterwards, type:

.. code-block:: bash

   module load python3   
   ./setup.sh
   
to start the installation. You should see the following output at the command line. 
    
    
.. code-block:: bash

   # Output of setup.sh
   Create tarball ...
   Job compilation script has been submitted to ecgate for installation in ${HOME}/flex_extract_vX.X
   You should get an email with subject "flexcompile" within the next few minutes!

    
The email content should look like this with a "SUCCESS" statement in the last line:

.. code-block:: bash

    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp phgrreal.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp grphreal.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp ftrafo.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g rwGRIB2.f90
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g posnam.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g preconvert.f90
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -g -O3 -o ./CONVERT2 ftrafo.o phgrreal.o grphreal.o rwGRIB2.o posnam.o preconvert.o -L/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3   
    -rwxr-x---. 1 USER at 353134 May 23 12:27 CONVERT2
    SUCCESS!    























.. _ref-gateway-mode:

Gateway mode
------------


.. _ref-req-gateway: 
 
Gateway environment requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The environment on your local system has to provide these software packages
and libraries, since ``flex_extract`` does only prepare the job script and send
it to the ECMWF servers:
    
* `Python3`_ or `Anaconda Python3`_
* `numpy`_
* `genshi`_
 

.. _ref-prep-gateway:

Prepare gateway environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to install all required packages is to use the package management system of your Linux distribution. To do so, it is necessary to use a user with admin rights.
The installation was tested on a *GNU/Linux Debian buster* and an *Ubuntu 18.04 Bionic Beaver* system.

.. code-block:: sh

   # On a Linux Debian or Ubuntu system do
   # (if not already available):
   apt-get install python3
   apt-get install pip
   apt-get install genshi
   apt-get install numpy


.. _ref-test-gateway:

Test gateway environment
^^^^^^^^^^^^^^^^^^^^^^^^
 
Check the availability of the python packages by typing ``python3`` in
a terminal window and run the ``import`` commands in the python shell. 
If there are no error messages, you succeeded in setting up the environment.

.. code-block:: python
    
   # check in python3 console
   import genshi
   import numpy
 


.. _ref-install-gateway:

Gateway installation
^^^^^^^^^^^^^^^^^^^^

In this mode, access to the ECMWF computing and archiving facilities is enabled through an ECaccess gateway server on a local member state server. The ECaccess framework is necessary to interactively submit jobs to the ECMWF batch system and to transfer files between ECMWF and local gateway server. 

Please see `ECMWF's instructions on gateway server`_ to establish the gateway server if not already in place.
Additionally, to be able to use the Ecaccess file transfer service **ectrans** please also create an association. 
The easiest way is to visit the ECaccess Member State Gateway website (e.g. msgatway.ecmwf.int) and follow the instructions in the short `ECaccess Presentation`_ (page 17 ff.). Additional documentation can be found on the `ECMWF ectrans site`_.

After everything is set up you have to create an *ecaccess certificate* to be able to send and receive files from and to the ECMWF server. You can do this by using the ``ecaccess-certificate-create`` command on the gateway server. You will be prompted for your ECMWF member state user name and a password (which will be usually generated by a Token). This certificate has to be re-newed periodically (every 7 days). 

.. code-block:: bash
   
   $ ecaccess-certificate-create
   Please enter your user-id: example_username
   Your passcode: ***
   
``Flex_extract`` will be run on an ECMWF server which makes the setup the same as for the **remote mode**. In the ``setup.sh`` script `[ref] <Documentation/Input/setup.html>`_, select the ``Makefile.gfortran`` for the ``CONVERT2`` Fortran program and the ECMWF server (*target*) you would like to use. 
The job script, send to the job queue via the ECaccess software, selects again automatically the correct libraries from the module system. For enableing the file transfer you have to set the *ECUID*, *ECGID*, *GATEWAY* and *DESTINATION* parameter values.
 

.. code-block:: bash
    :caption: 'Example settings for a gateway installation.'
    :name: setup.sh
    
    # -----------------------------------------------------------------
    # AVAILABLE COMMANDLINE ARGUMENTS TO SET
    #
    # THE USER HAS TO SPECIFY THESE PARAMETER
    #
    TARGET='ecgate'
    MAKEFILE='Makefile.gfortran'
    ECUID='uid'
    ECGID='gid'
    GATEWAY='server.example.edu'
    DESTINATION='example@genericSftp'
    INSTALLDIR=None
    JOB_TEMPLATE='job.template'
    CONTROLFILE='CONTROL_EA5'


Afterwards, type:

.. code-block:: bash

   $ ./setup.sh
   
to start the installation. You should see the following output at the command line. 
    
    
.. code-block:: bash

   # Output of setup.sh
   Create tarball ...
   Job compilation script has been submitted to ecgate for installation in ${HOME}/flex_extract_vX.X
   You should get an email with subject "flexcompile" within the next few minutes!

    
The email content should look like this with a "SUCCESS" statement in the last line:

.. code-block:: bash

    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp phgrreal.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp grphreal.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp ftrafo.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g rwGRIB2.f90
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g posnam.f
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -I. -I/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/include -g preconvert.f90
    gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -g -O3 -o ./CONVERT2 ftrafo.o phgrreal.o grphreal.o rwGRIB2.o posnam.o preconvert.o -L/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.12.0/GNU/6.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3   
    -rwxr-x---. 1 USER at 353134 May 23 12:27 CONVERT2
    SUCCESS!    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
.. _ref-local-mode:

Local mode
----------



.. _ref-req-local: 
 
Local environment requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For the local access modes **member** and **public** there is no difference in 
the installation process.

The environment on your local system has to provide these software packages
and libraries, since all extraction and preparation is done at the local system:

+------------------------------------------------+-----------------+
|  Python part                                   | Fortran part    |
+------------------------------------------------+-----------------+
| * `Python3`_                                   | * `gfortran`_   |
| * `numpy`_                                     | * `fftw3`_      |
| * `genshi`_                                    | * `eccodes`_    |
| * `eccodes for python`_                        | * `emoslib`_    |
| * `ecmwf-api-client`_ (everything except ERA5) |                 |
| * `cdsapi`_ (just for ERA5)                    |                 |
+------------------------------------------------+-----------------+


.. _ref-prep-local:

Prepare local environment
^^^^^^^^^^^^^^^^^^^^^^^^^

The easiest way to install all required packages is to use the package management system of your Linux distribution. To do so, it is necessary to use a user with admin rights.
The installation was tested on a *Debian GNU/Linux buster/sid* and an *Ubuntu 18.04 Bionic Beaver* system.

.. code-block:: sh

   # On a Linux Debian or Ubuntu system do
   # (if not already available):
   apt-get install python3 (usually available on normal Linux systems)
   apt-get install pip
   apt-get install gfortran
   apt-get install fftw3-dev 
   apt-get install libeccodes-dev
   apt-get install libemos-dev 
   apt-get install python3-eccodes
   apt-get install genshi
   apt-get install numpy
   pip install cdsapi 
   pip install ecmwf-api-client 

.. note::

    In case you would like to use Anaconda Python we recommend you follow the installation instructions of 
    `Anaconda Python Installation for Linux <https://docs.anaconda.com/anaconda/install/linux/>`_ and then install the
    ``eccodes`` package from ``conda`` with:

    .. code-block:: bash

       conda install conda-forge::python-eccodes


The CDS API (cdsapi) and the ECMWF Web API (ecmwf-api-client) have both to be installed since ERA5 can only be retrieved with the ``CDS API`` and all other datasets with the ``ECMWF Web API``.     
       
.. note:: 

    Since **public users** currently don't have access to the full *ERA5* dataset they can skip the installation of the ``CDS API``. 
    
Both user groups have to provide key's with their credentials for the Web API's in their home directory. Therefore, follow these instructions:
   
ECMWF Web API:
   Go to `MARS access`_ website and log in with your credentials. Afterwards, on this site in section "Install ECMWF KEY" the key for the ECMWF Web API should be listed. Please follow the instructions in this section under point 1 (save the key in a file `.ecmwfapirc` in your home directory). 
     
CDS API:
   Go to 'CDS API registration'_ and register there too. Log in at the `cdsapi`_ website and follow the instructions at section "Install the CDS API key" to save your credentials in a `.cdsapirc` file.
     

.. _ref-test-local:
   
Test local environment
^^^^^^^^^^^^^^^^^^^^^^

Check the availability of the system packages with ``dpkg -s <package-name> |  grep Status`` or ``rpm -q <package_name>``, depending on your system. For example: 

.. code-block:: sh

   $ dpkg -s libeccodes-dev |  grep Status
   # or
   $ rpm -q libeccodes-dev
 
Afterwards, check the availability of the python packages by typing ``python3`` in
a terminal window and run the ``import`` commands in the python shell. If there are no error messages, you succeeded in setting up the environment.

.. code-block:: python
    
   # check in python3 console
   import eccodes
   import genshi
   import numpy
   import cdsapi
   import ecmwfapi
   


Test the Web API's
""""""""""""""""""

You can start very simple test retrievals for both Web API's to be sure that everything works. This is recommended to minimize the range of possible errors using ``flex_extract`` later on.

ECMWF Web API
"""""""""""""


+----------------------------------------------------------+----------------------------------------------------------+
|Please use this piece of python code for **Member user**: |Please use this piece of python code for **Public user**: |
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
"""""""

Since ERA5 extraction with CDS API might take some time due to the very high number of requests, you can start by retrieving some online stored pressure levels (not from MARS). This is usually much faster and gives a quick result to find out if the web API works:

Please use this piece of python code to retrieve a small sample of *ERA5* pressure levels:

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


Afterwards, when you know that the CDS API generally works, you can try to extract some
data from the MARS archive. From the latest experience we know that this can take a while.    

.. **Member user**

Please use this piece of python code to retrieve a small *ERA5* data sample as a **member user**! The **public user** doesn't have access to the full *ERA5* dataset!

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
    Please use this piece of python code: 

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
^^^^^^^^^^^^^^^^^^

First prepare the Fortran ``Makefile`` for your environment and set it
in the ``setup.sh`` script. (See section :ref:`ref-convert` for information on 
the Fortran program.)
``flex_extract`` has already two ``Makefiles`` prepared for te ``gfortran`` and 
the ``ifort`` compiler:

 * Makefile.local.gfortran
 * Makefile.local.ifort

They can be found in the path ``flex_extract_vX.X/source/fortran``, where
``vX.X`` should be substituted with the current version number.

.. caution::   
   It is necessary to adapt **ECCODES_INCLUDE_DIR** and **ECCODES_LIB** in these
   ``Makefiles``.


So starting from the root directory of ``flex_extract``, 
go to the ``Fortran`` source directory and open the ``Makefile`` of your 
choice to modify with an editor of your choice. We use the ``nedit`` in this case.

.. code-block:: bash 

   cd flex_extract_vX.X/source/fortran
   nedit Makefile.local.gfortran

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

   # these are the paths on a current Debian 10 Testing system (May 2019)
   ECCODES_INCLUDE_DIR=/usr/lib/x86_64-linux-gnu/fortran/gfortran-mod-15/
   ECCODES_LIB= -L/usr/lib -leccodes_f90 -leccodes -lm  
   
    
The Fortran program called ``CONVERT2`` will be compiled during the 
installation process to get an executable. Therefore the ``Makefile``
has to be set in the ``setup.sh`` script.

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
   MAKEFILE='Makefile.local.gfortran'
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
   
to start the installation. You should see the following output at the command line. 
    
    
.. code-block:: bash

   # Output of setup.sh   
   WARNING: installdir has not been specified
   flex_extract will be installed in here by compiling the Fortran source in /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1/source/fortran
   Install flex_extract_v7.1 software at local in directory /raid60/nas/tmc/Anne/Interpolation/flexextract/flex_extract_v7.1

   Using makefile: Makefile.local.gfortran
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp phgrreal.f
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp grphreal.f
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -g -O3 -fopenmp ftrafo.f
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -fopenmp -I. -I/usr/local/gcc-4.9.3/grib_api-1.14.3/include -O3 rwGRIB2.f90
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -fopenmp -I. -I/usr/local/gcc-4.9.3/grib_api-1.14.3/include -O3 posnam.f
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -c -O3 -fopenmp -I. -I/usr/local/gcc-4.9.3/grib_api-1.14.3/include -O3 preconvert.f90
   gfortran   -m64 -fdefault-real-8 -fcray-pointer -fno-second-underscore  -ffixed-line-length-132 -fopenmp  -fconvert=big-endian  -O3 -O3 -fopenmp -o ./CONVERT2 ftrafo.o phgrreal.o grphreal.o rwGRIB2.o posnam.o preconvert.o -L/usr/local/gcc-4.9.3/grib_api-1.14.3/lib -Bstatic  -lgrib_api_f77 -lgrib_api_f90 -lgrib_api -Bdynamic  -lm  -ljasper -lemosR64

   -rwxrwxr-x. 1 philipa8 tmc 282992 May 23 22:27 ./CONVERT2






``Flex_extract`` in combination with ``FLEXPART``
=================================================

Some users might like to incorporate ``flex_extract`` directly into the ``FLEXPART``
distribution. Then the installation path has to be changed by setting the parameter
`installdir` in the ``setup.sh`` file to the ``script`` directory in the ``FLEXPART`` root directoy. 









.. _ref-testinstallfe:

Test installation
=================

Fortran program test
--------------------

To check if the compilation of the Fortran program ``CONVERT2`` was successful
a quick program call on a minimal prepared dataset can be done.

For this, go from the ``flex_extract`` root directory to the test 
directory and call the executable of the Fortran program.

.. note:: 
   Remember that you might have to log in at the ECMWF server if you used the installation for the **remote** or **gateway** mode. There you find the ``flex_extract`` root directory in your ``$HOME`` directory.

.. code-block:: bash
   
   cd test/Installation/Convert
   # call the Fortran progam without arguments
   ../../../source/fortran/CONVERT2

The installation was successfull if it showed the following output:

.. code-block:: bash

    readspectral:            1  records read
    readlatlon:            8  records read
   STATISTICS:  98842.4598 98709.7359  5120.5385
    readlatlon:            4  records read
    readlatlon:            4  records read
    readlatlon:            4  records read
   SUCCESSFULLY FINISHED CONVERT_PRE: CONGRATULATIONS

Now go back to the root directoy:

.. code-block:: bash
   
   $ cd ../../../
   


Full test
---------

    see :doc:`quick_start`

    
