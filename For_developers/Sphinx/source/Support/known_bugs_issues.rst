Known Bugs and Issues
*********************

Release v7.1
============


CDS API and ERA5 data
---------------------

  See ticket `#230 <https://www.flexpart.eu/ticket/230>`_  on flexpart.eu for information.


Installation problems with ``GATEWAY`` and ``DESTINATION`` parameters
---------------------------------------------------------------------

  See ticket `#263 <https://www.flexpart.eu/ticket/263>`_  on flexpart.eu for information.


Installation problems with the Fortran program ``calc_etadot``
--------------------------------------------------------------

   See ticket `#264 <https://www.flexpart.eu/ticket/264>`_  on flexpart.eu for information.

ECCODES Error Code 250
----------------------

If you get an error message from ECCODES with code 250, locking like this:

.. code-block:: bash

	ECCODES ERROR   :   wrong size (184) for pv it contains 276 values 
	ECCODES ERROR   :  get: pv Passed array is too small
	... ERROR CODE: 250
	... ERROR MESSAGE:
	 	 Command '['<path-to-flex_extract>/flex_extract_v7.1/Source/Fortran/calc_etadot']' returned non-zero exit status 250.
	... FORTRAN PROGRAM FAILED!

then you have set a wrong maximum level in the :literal:`CONTROL` file! 
It is important to properly select the maximum level depending on the data set you would like to retrieve. The following model level definitions (number of model levels available) are limited to [16, 19, 31, 40, 50, 60, 62, 91, 137]. The ERA-Interim data set uses 62 model levels and *ERA5* as well as *CERA-20C* uses 137. The operational data set uses different model levels depending on the date. For example, on the 25/06/2013 the operational system started to use 137 model levels. Therefore, everytime you extract data from a date later than 25/06/2013 you have to select LEVEL=137 in the :literal:`CONTROL` file or define a LEVELLIST=1/to/137. Of course you can stop before the top of the atmosphere, such as 60/to/137, but you have to select the maximum level number as the last one. Table 2 in the `scientific model description paper <https://www.geosci-model-dev-discuss.net/gmd-2019-358/>`_ gives an overview of the level lists and the corresponding introducstion date. 


.. note::
 
	Remember that model level 1 corresponds to the top of the atmosphere and then increases in the direction of the surface.
