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



The ``flex_extract`` software package contains python and shell scripts as well as a Fortran program. These components rely on several libraries which need to be available before starting the installation process. Currently, the software is only tested for a GNU/Linux environment. Feel free to try it out on other platforms.

At first, find out to which `user group <Ecmwf/access.html>`_ you belong and follow the instructions at :ref:`ref-registration` to obtain an account at ECMWF (if you don't have it already). Depending on the user group and the way to access the ECWMF MARS archive, there are four possible :doc:`Documentation/Overview/app_modes`:  

- Remote (member-state users only) :ref:`[installation]<ref-remote-mode>`
- Gateway (member-state users only) :ref:`[installation]<ref-gateway-mode>`
- Local, member-state user :ref:`[installation]<ref-local-mode>`
- Local, public user :ref:`[installation]<ref-local-mode>`

More information can be found in :doc:`Documentation/Overview/app_modes`.

.. note::

   If you encounter any problems in the installation process, you can ask for :doc:`support`.





.. _ref-registration:

Registration at ECMWF
=====================

The registration depends on the :doc:`Documentation/Overview/app_modes` and in case of the local mode also on the data set you'd like to retrieve. The following table gives an overview where you need to register. 

+--------------+------------------------------------+--------------+
|              |  Member-state user                 | Public user  |
|              +---------+----------+---------------+--------------+
|    Data sets |Remote   |Gateway   |Local          | Local        |
+--------------+---------+----------+---------------+--------------+
| Operational  | 1       | 1        | 1,2           | -            |
+--------------+---------+----------+---------------+--------------+
| ERA-Interim  | 1       | 1        | 1,2           | 2            |
+--------------+---------+----------+---------------+--------------+
| CERA-20C     | 1       | 1        | 1,2           | 2            |
+--------------+---------+----------+---------------+--------------+
| ERA5         | 1       | 1        | 3             | -            |
+--------------+---------+----------+---------------+--------------+



Registration options:

    1.)  Access through a member-state user account granted by the `Computing Representative`_. The credentials have to be provided during installation.
    
    2.)  Access through the ECMWF Web API. Need to sign in at `ECMWF Web API <https://confluence.ecmwf.int/display/WEBAPI/ECMWF+Web+API+Home>`_ and configure the ECMWF key as described. Member-state users can sign in with their credentials from the `Computing Representative`_ and public users have to fill out the `registration form`_ to get an account.
    
    3.) Access through the `CDS API <https://cds.climate.copernicus.eu/api-how-to>`_. Extra registration for member-state users is required at `Copernicus Climate Data Store <https://cds.climate.copernicus.eu/user/register>`_ including the configurations of the CDS key as described. This mode is currently not available for public users. See the note at `user group <Ecmwf/access.html>`_ for information.

    
    
.. _ref-licence:
    
Accept licences for public datasets
=====================================

Each ECMWF :underline:`public` dataset has its own licence whose acceptance requires user activity, regardless of the user group. 

For the *ERA-Interim* and *CERA-20C* datasets this can be done at the ECMWF website `Available ECMWF Public Datasets <https://confluence.ecmwf.int/display/WEBAPI/Available+ECMWF+Public+Datasets>`_. Log in and follow the licence links on the right side for each dataset and accept it.
    
For the *ERA5* dataset this has to be done at the `Climate Data Store (CDS) website <https://cds.climate.copernicus.eu/cdsapp#!/search?type=dataset>`_. Log in and select, on the left panel, product type "Reanalysis" for finding *ERA5* datasets. Then follow any link with *ERA5* to the full dataset record, click on tab "Download data" and scroll down. There is a section "Terms of use" where you have to click the :underline:`Accept terms` button.
   




.. _ref-download:

Download ``flex_extract``
=========================

There are two options to download ``flex_extract``:

tar ball
    You can download a tar ball with the latest release from the `flex_extract page <https://www.flexpart.eu/wiki/FpInputMetEcmwf>`_ from our ``FLEXPART`` community website and then untar the file. 
  
    .. code-block:: bash
       
       tar -xvf <flex_extract_vX.X.tar>

git repo  
    Alternatively, if you have ``git`` installed on your machine, and if you are interested to keep the code in a version control system, you may clone the latest version from our git repository master branch.  

    .. code-block:: bash

       $ git clone --single-branch --branch master https://www.flexpart.eu/gitmob/flex_extract





.. _ref-requirements: 
 
Dependencies
============

The software required to run ``flex_extract`` depends on the :doc:`Documentation/Overview/app_modes` and therefore is described in the respective specific installation sections. 
    
Generally speaking, ``flex_extract`` requires `Python 3`_ and Fortran together with certain modules / libraries.
We tested ``flex_extract`` with the Python3 package from the the GNU/Linux distribution and Anaconda Python. The required Python3 modules should prefarably be installed as distribution packages, or alternatively using Python's own package manager ``pip`` (this may mess up some aspects of your python installation, especially if you use ``pip`` as root. Think about using virtual environments.).

Before installing the system packages check the availability with (Debian-based system) ``dpkg -s <package-name> |  grep Status`` or (Redhat-based system) ``rpm -q <package_name>``. For example: 

.. code-block:: sh

   $ dpkg -s libeccodes-dev |  grep Status
   # or
   $ rpm -q libeccodes-dev



.. _ref-install-fe:

Installation of ``flex_extract``
================================

The actual installation of ``flex_extract`` is done by executing a shell script called ``setup.sh``.
It defines some parameters and calls a Python script passing the parameters as command line arguments. For details, see :doc:`Documentation/Input/setup`. 

For each application mode installation section we describe the requirements for the explicit 
environment and how it is installed, test if it works and how the actual ``flex_extract``
installation has to be done. At the users local side not all software has to be present for ``flex_extract``.


Select one of the following modes to install:

    :doc:`Installation/remote`
    
    :doc:`Installation/gateway`
    
    :doc:`Installation/local`


.. toctree::
    :hidden:
    :maxdepth: 2
    
    Installation/remote
    Installation/gateway
    Installation/local

    

``Flex_extract`` in combination with ``FLEXPART``
=================================================

Some users might wish to incorporate ``flex_extract`` directly into the ``FLEXPART`` distribution. Then the installation path has to be changed by setting the parameter `installdir` in the ``setup.sh`` file to the ``script`` directory in the ``FLEXPART`` root directoy. 


.. _ref-testinstallfe:

Test installation
=================

Fortran program test
--------------------

To check whether the Fortran program ``calc_etadot`` has been compiled and runs properly, it can be applied to a prepared minimal dataset.

For this, go from the ``flex_extract`` root directory to the ``Testing/Installation/Calc_etadot/`` directory and execute the Fortran program.

.. note:: 
   Remember that you might have to log in at the ECMWF server if you used the installation for the **remote** or **gateway** mode. There you find the ``flex_extract`` root directory in your ``$HOME`` directory.

.. code-block:: bash
   
   cd Testing/Installation/Calc_etadot
   # execute the Fortran progam without arguments
   ../../../Source/Fortran/calc_etadot

The installation was successfull if you obtain on standard output:

.. code-block:: bash
    
    STATISTICS:          98842.4598  98709.7359   5120.5385
    STOP SUCCESSFULLY FINISHED calc_etadot: CONGRATULATIONS


Now go back to the root directory:

.. code-block:: bash
   
   $ cd ../../../
   


Full test
---------

    see :doc:`quick_start`

    
