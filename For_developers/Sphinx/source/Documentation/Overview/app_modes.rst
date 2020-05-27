*****************
Application modes
*****************

.. role:: underline
    :class: underline
        
.. _member state: https://www.ecmwf.int/en/about/who-we-are/member-states 
.. _instructions: https://apps.ecmwf.int/registration/
.. _ECMWF's instructions on gateway server: https://confluence.ecmwf.int/display/ECAC/ECaccess+Home

    
.. _ref-app-modes:

Arising from the two user groups described in :doc:`../../Ecmwf/access`, ``flex_extract`` has four different :underline:`user application modes`:

.. _ref-remote-desc:

  1. Remote (member)
      In the **Remote mode** the user works directly on a ECMWF member-state Linux server, such as ``ecgate`` or ``cca/ccb``. The software will be installed in the ``$HOME`` directory. The user does not need to install any of the third-party libraries mentioned in :ref:`ref-requirements`, as ECMWF provides everything with environment modules. The module selection will be done automatically by ``flex_extract``. 
      
.. _ref-gateway-desc:
      
  2. Gateway (member)
      The **Gateway mode** can be used if a local member-state gateway server is in place. Then, the job scripts can be submitted to the ECMWF member-state Linux server via the ECMWF web access tool ``ecaccess``. The installation script of ``flex_extract`` must be executed on the local gateway server such that the software will be installed in the ``$HOME`` directory at the ECMWF server and that some extra setup is done in the ``flex_extract`` directory on the local gateway server. For more information about establishing a gateway server, please refer to `ECMWF's instructions on gateway server`_. For the **Gateway mode** the necessary environment has to be established which is described in :ref:`ref-prep-gateway`.

.. _ref-local-desc:
      
  3. Local member
      Scripts are installed and executed on a local machine, either in the current ``flex_extract`` directory or in a path given to the installation script. Under this scenario, a software environment similar to that at ECMWF is required. Additionally, web API's have to be installed to access ECMWF server. The complete installation process is described in :ref:`ref-local-mode`.
      
  4. Local public
      Scripts are installed and executed on a local machine, either in the current ``flex_extract`` directory or in a path given to the installation script. Under this scenario, a software environment similar to that at ECMWF is required. Additionally, web API's have to be installed to access ECMWF servers. The complete installation process is described in :ref:`ref-local-mode`. In this case, a direct registration at ECMWF is necessary and the user has to accept a specific license agreement for each dataset he/she intends to retrieve. 
      
      
An overview is sketched in figure :ref:`ref-fig-marsaccess`.

.. _ref-fig-marsaccess:

.. figure:: ../../_static/Diagramm_MarsAccess2.png

   Application modes 


    
.. toctree::
    :hidden:
    :maxdepth: 2
