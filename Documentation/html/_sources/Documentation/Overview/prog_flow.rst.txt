************
Program Flow
************




General program flow
====================


The following flow diagram shows the general steps performed by ``flex_extract``. 
    
.. _ref-fig-submit:

.. figure:: ../../_files/submit.png    
    
    Overview of the call of python's ``submit.py`` script and raw sequence of working steps done in ``flex_extract``.

    
The ``submit.py`` Python program is called by the Shell script ``run.sh`` or ``run_local.sh`` and accomplish the following steps: 

    1. Setup the control data:
        It gets all command-line and ``CONTROL`` file parameters as well as optionally the ECMWF user credentials. Depending the :doc:`app_modes`, it might also prepare a job script which is then send to the ECMWF queue. 
    2. Retrieves data from MARS:
        It creates and sends MARS-requests either on the local machine or on ECMWF server, that receives the data and stores them in a specific format in GRIB files. If the parameter ``REQUEST`` was set ``1`` the data are not received but a file ``mars_requests.csv`` is created with a list of MARS requests and their settings. If it is set to ``2`` the file is created in addition to retrieving the data. The requests are created in an optimised way by splitting in time, jobs  and parameters.   
    3. Post-process data to create final ``FLEXPART`` input files:
        After all data is retrieved, the disaggregation of flux fields (`see here <../disagg.html>`_ ) is done as well as the calculation of vertical velocity (`see here <../vertco.html>`_) by the Fortran program ``calc_etadot``. Eventually, the GRIB fields are merged together such that a single grib file per time step is available with all fields for ``FLEXPART``. Since model level fields are typically in *GRIB2* format whereas surface level fields are still in *GRIB1* format, they can be converted into GRIB2 if parameter ``FORMAT`` is set to *GRIB2*. Please note, however, that older versions of FLEXPART may have difficulties reading pure *GRIB2* files since some parameter IDs change in *GRIB2*. If the retrieval is executed remotely at ECMWF, the resulting files can be communicated to the local gateway server via the ``ECtrans`` utility if the parameter ``ECTRANS`` is set to ``1`` and the parameters ``GATEWAY``, ``DESTINATION`` have been set properly during installation. The status of the transfer can be checked with the command ``ecaccess-ectrans-list`` (on the local gateway server). If the script is executed locally the progress of the script can be followed with the usual Linux tools.



Workflows of different application modes
========================================

More details on how different the program flow is for the different :doc:`app_modes` is sketched in the following diagrams:  

+-------------------------------------------------+------------------------------------------------+
| .. figure:: ../../_files/mode_remote.png        | .. figure:: ../../_files/mode_gateway.png      |
+-------------------------------------------------+------------------------------------------------+   

+-------------------------------------------------+------------------------------------------------+
| .. figure:: ../../_files/mode_local_member.png  | .. figure:: ../../_files/mode_local_public.png |
+-------------------------------------------------+------------------------------------------------+   


Example application setting for a local member user
===================================================

.. figure:: ../../_files/ex_runlocal_en.png  




.. toctree::
    :hidden:
    :maxdepth: 2
