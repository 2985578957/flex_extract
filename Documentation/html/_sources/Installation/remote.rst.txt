************************
Remote mode installation
************************

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


.. _ref-remote-mode: 


.. _ref-req-remote: 
 
Remote mode - dependencies
==========================

The following software is required, and already available at the ECMWF servers:
    
+---------------------------+-----------------+
|  Python code              | Fortran code    |
+---------------------------+-----------------+
| * `Python3`_              | * `gfortran`_   |
| * `numpy`_                | * `fftw3`_      |
| * `genshi`_               | * `eccodes`_    |
| * `eccodes for python`_   | * `emoslib`_    |
+---------------------------+-----------------+


.. _ref-prep-remote:

Prepare remote environment
==========================
 
ECMWF servers provide all libraries via a module system. Loading the required modules is already built into ``flex_extract`` and no user action is needed.


.. _ref-install-remote:

Remote installation
===================

First, log in on one of the ECMWF servers, such as *ecgate* or *cca/ccb*. 
Substitute *<ecuid>* with your ECMWF user name:

.. code-block:: bash
   
   ssh -X <ecuid>@ecaccess.ecmwf.int

This will lead to the following output on the command line, asking for your password:
   
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

   <ecuid>@<ipname/address>'s password: ***
   Select hostname (ecgate, cca, ccb) [ecgate]: ecgate

   [<ecuid>@ecgb11 ~]$ 
   
Substitute the *<localuser>* and *<localmachine.tld>* placeholders with your local user name and the IP name or address of your local machine. 
Untar the file and change into the ``flex_extract`` root directory. 
   
.. code-block:: bash

   scp <localuser>@<localmachine.tld>:</path/to/tarfile/>flex_extract_vX.X.tar.gz  $HOME/
   cd $HOME
   tar xvf flex_extract_vX.X.tar.gz
   cd flex_extract_vX.X
   

   
Execute the ``setup.sh`` script from the ``flex_extract``'s root directory. 
Before executing it, it is necessary to adapt some parameters from ``setup.sh``
described in :doc:`../Documentation/Input/setup`. 

Open ``setup.sh`` with your preferred editor (e.g., nano) and adapt the values:  
   
+----------------------------------------------+----------------------------------------------+   
|   Use this for target = **ectrans**          |   Use this for target = **cca** or **ccb**   | 
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
|   MAKEFILE='makefile_ecgate'                 |   MAKEFILE='makefile_cray'                   |  
|   ECUID='<username>'                         |   ECUID='<username>'                         |  
|   ECGID='<groupID>'                          |   ECGID='<groupID>'                          |
|   GATEWAY='<gatewayname>'                    |   GATEWAY='<gatewayname>'                    |
|   DESTINATION='<username>@genericSftp'       |   DESTINATION='<username>@genericSftp'       | 
|   INSTALLDIR=None                            |   INSTALLDIR=''                              | 
|   JOB_TEMPLATE='installscript.template'      |   JOB_TEMPLATE='installscript.template'      |
|   CONTROLFILE='CONTROL_EA5'                  |   CONTROLFILE='CONTROL_EA5'                  | 
|   ...                                        |   ...                                        |   
+----------------------------------------------+----------------------------------------------+

:underline:`Please substitute the values of ECUID and ECGID
with your own ones (look at any of your files with ``ls -l'' to see uid and gid).`

.. note::

   If a local gateway server is available, files can be transferred with ``ECaccess`` commands. In that case, a valid *GATEWAY* and *DESTINATION* have to be present in the ``setup.sh`` file (even if not used, the lines must not be deleted). 

Afterwards, type:

.. code-block:: bash
  
   ./setup.sh
   
to start the installation. You should see the following on standard output. 
    
    
.. code-block:: bash

   # Output of setup.sh
   Create tarball ...
   Job compilation script has been submitted to ecgate for installation in ${HOME}/flex_extract_vX.X
   You should get an email with subject "flexcompile" within the next few minutes!

    
``Flex_extract`` automatically uses the email address connected to the user account on ECMWF servers. The email content should look like this with a "SUCCESS" statement in the last line:

.. code-block:: bash

    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./rwgrib2.f90
    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./phgrreal.f90
    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./grphreal.f90
    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./ftrafo.f90
    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./calc_etadot.f90
    gfortran    -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -I. -I/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/include -fdefault-real-8 -fopenmp -fconvert=big-endian   -c    ./posnam.f90
    gfortran   rwgrib2.o calc_etadot.o ftrafo.o grphreal.o posnam.o phgrreal.o -o calc_etadot_fast.out  -O3 -march=native -L/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -Wl,-rpath,/usr/local/apps/eccodes/2.13.0/GNU/7.3.0/lib -leccodes_f90 -leccodes -ljasper -lpthread -L/usr/local/apps/jasper/1.900.1/LP64/lib -ljasper -lm -L/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -Wl,-rpath,/usr/local/apps/libemos/000455/GNU/6.3.0/lib  -lemos.R64.D64.I32 -L/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -Wl,-rpath,/usr/local/apps/fftw/3.3.4/GNU/6.3.0/lib -lfftw3    -fopenmp
    ln -sf calc_etadot_fast.out calc_etadot
    lrwxrwxrwx. 1 <username> at 20 Mar  8 14:11 calc_etadot -> calc_etadot_fast.out
    SUCCESS!
    
