************
Access Modes
************

.. _public datasets: https://confluence.ecmwf.int/display/WEBAPI/Available+ECMWF+Public+Datasets
.. _Computing Representative: https://www.ecmwf.int/en/about/contact-us/computing-representatives
.. _Climate Data Store: https://cds.climate.copernicus.eu
.. _CDS API: https://cds.climate.copernicus.eu/api-how-to

Access to the ECMWF Mars archive is divided into two groups: **member state** users and **public** users.

**Member state user**: 
    This access mode allows the user to work directly on the ECMWF Linux Member State Servers or via a Web Access Toolkit ``ecaccess`` through a local Member State Gateway Server. This enables the user to have direct and full access to the Mars archive. There might be some limitations in user rights such as the declined access to the latest forecasts. This has to be discussed with the `Computing Representative`_. This user group is also able to work from their local facilities without a gateway server in the same way a **public** user would. The only difference is the connection with the Web API. However, this is automatically selected by ``flex_extract``.
    

**Public user**: 
    This access mode allows every user to access the ECMWF `public datasets`_ from their local facilities. ``Flex_extract`` is able (tested for the use with ``FLEXPART``) to extract the re-analysis datasets such as ERA-Interim and CERA-20C. The main difference to the **member state user** is the method of access with the Web API and the availability of data. For example, in ERA-Interim there is only a 6-hourly temporal resolution instead of 3 hours. The access method is selected by providing the command line argument "public=1" and providing the MARS keyword "dataset" in the ``CONTROL`` file. Also, the user has to explicitly accept the license of the dataset to be retrieved. This can be done as described in the installation process at section :ref:`ref-licence`.   
     
.. note::
    
   The availability of the public dataset *ERA5* with the ECMWF Web API was cancelled in March 2019. The oportunity of local retrieval of this dataset was moved to the `Climate Data Store`_ which uses another Web API named `CDS API`_. This Data Store stores the data on explicit webservers for faster and easier access. Unfortunately, for *ERA5* there are only surface level and pressure level data available for *public users*. In the case of a *member user* it is possible to bypass the request to the MARS archive from ECMWF to retrieve the data. ``Flex_extract`` is already modified to use this API so *member user* can already retrieve *ERA5* data while *public users* have to wait until model level are available. 
        
For information on how to register see :ref:`ref-registration`. 

.. toctree::
    :hidden:
    :maxdepth: 2
