************
Access Modes
************

.. _public datasets: https://confluence.ecmwf.int/display/WEBAPI/Available+ECMWF+Public+Datasets
.. _Computing Representative: https://www.ecmwf.int/en/about/contact-us/computing-representatives

Access to the ECMWF Mars archive is divided into two groups: **member state** users and **public** users.

**Member state user**: 
    This access mode allows the user to work directly on the ECMWF Linux Member State Servers or via a Web Access Toolkit ``ecaccess`` through a local Member State Gateway Server. This enables the user to have direct and full access to the Mars archive. There might be some limitations in user rights such as the declined access to the latest forecasts. This has to be discussed with the `Computing Representative`_. This user group is also able to work from their local facilities without a gateway server in the same way a **public** user would. The only difference is the method of Web API which is automatically selected by ``flex_extract``.
    

**Public user**: 
    This access mode allows every user to access the ECMWF `public datasets`_ from their local facilities. ``Flex_extract`` is able (tested for the use with ``FLEXPART``) to extract the re-analysis datasets such as ERA5, ERA-Interim and CERA-20C. The main difference to the **member state user** is the method of access with the Web API and the availability of data. For example, in ERA-Interim there is only a 6-hourly temporal resolution instead of 3 hours. The access method is selected by providing the command line argument "public=1" and providing the Mars keyword "dataset" in the ``CONTROL`` file. Also, the user has to explicitly accept the license of the dataset to be retrieved. This can be done as described in the installation process at section :ref:`ref-licence`.   
        
For information on how to register see :ref:`ref-registration`. 

.. toctree::
    :hidden:
    :maxdepth: 2