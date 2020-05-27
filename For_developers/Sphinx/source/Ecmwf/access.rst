************
Access modes
************

.. _public datasets: https://confluence.ecmwf.int/display/WEBAPI/Available+ECMWF+Public+Datasets
.. _Computing Representative: https://www.ecmwf.int/en/about/contact-us/computing-representatives
.. _Climate Data Store: https://cds.climate.copernicus.eu
.. _CDS API: https://cds.climate.copernicus.eu/api-how-to

Access to the ECMWF MARS archive is divided into two groups: **member state** users and **public** users.

**Member-state user**: 
    This access mode allows the user to work directly on a ECMWF member-state Linux server or via the ``ecaccess`` Web-Access Toolkit through a local member-state Gateway server. This enables the user to have direct and full access to the MARS archive. There might be some limitations in user rights, such as no access to the latest forecasts. In case such data are needed, this has to be agreed upon with the national `Computing Representative`_. This user group is also able to work from their local facilities without a gateway server in the same way a **public** user would. The only difference is the connection with the Web API, which, however, is automatically selected by ``flex_extract``.
    

**Public user**: 
    This access mode allows every user to access the ECMWF `public datasets`_ from their local facilities. ``Flex_extract`` is able to extract the re-analysis datasets such as ERA-Interim and CERA-20C for use with ``FLEXPART`` (tested). The main difference to the **member-state user** is the method of access with the Web API and the availability of data. For example, in ERA-Interim,  only a 6-hourly temporal resolution is available instead of 3 hours. The access method is selected by providing the command line argument "public=1" and providing the MARS keyword "dataset" in the ``CONTROL`` file. Also, the user has to explicitly accept the license of the data set to be retrieved. This can be done as described in the installation process at section :ref:`ref-licence`.   
     
.. note::
    
   The availability of the public dataset *ERA5* with the ECMWF Web API was cancelled by ECWMF in March 2019. Local retrieval of this dataset now has to use the `Climate Data Store`_ (CDS) with a different Web API called `CDS API`_. CDS stores the data on dedicated web servers for faster and easier access. Unfortunately, for *ERA5*, only surface level and pressure level data are available for *public users* which is not enough to run FLEXPART. For a *member user*, it is possible to pass the request to the MARS archive to retrieve the data. ``Flex_extract`` is already modified to use this API so a *member user* can already retrieve *ERA5* data for FLEXPART while *public users* have to wait until model level are made available. 
        
For information on how to register see :ref:`ref-registration`. 

.. toctree::
    :hidden:
    :maxdepth: 2
