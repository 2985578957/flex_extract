****************************************
ECMWF user credential file ``ECMWF_ENV``
****************************************

This file contains the user credentials for working on ECMWF servers and transferring files between the ECMWF servers and the local gateway server. It is located in the ``flex_extract_vX.X/Run`` directory and will be created in the installation process for the application modes **remote** and **gateway**.

This file is based on the template ``ECMWF_ENV.template`` which is located in the ``templates`` directory.

.. note::
 
   In the **local** mode this file is not present.



Content of ``ECMWF_ENV``
------------------------

An example of the content of an ``ECMWF_ENV`` file is shown below:
  
.. code-block:: bash

   ECUID user_name
   ECGID user_group
   GATEWAY gateway_name
   DESTINATION destination_name
   
   

.. toctree::
    :hidden:
    :maxdepth: 2
