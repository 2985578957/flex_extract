================
The CONTROL file
================
    
  

.. MARS user documentation https://confluence.ecmwf.int/display/UDOC/MARS+user+documentation
.. MARS keywords and explanation https://confluence.ecmwf.int/display/UDOC/MARS+keywords
 
 
This file is an input file for :literal:`flex_extract's` main script :literal:`submit.py`.
It contains the controlling parameters which :literal:`flex_extract` needs to decide on data set specifications,
handling of the  data retrieved, and general behaviour. The naming convention is usually (but not necessarily):

   :literal:`CONTROL_<Dataset>[.optionalIndications]`

There are a number of data sets for which the procedures have been tested, the operational data and the re-analysis datasets CERA-20C, ERA5, and ERA-Interim.
The optional indications for the re-analysis data sets mark the files for *public users* 
and *global* domain. For the operational data sets (*OD*), the file names contain also information of
the stream, the field type for forecasts, the method for extracting the vertical wind, and other information such as temporal or horizontal resolution.


Format of CONTROL files
----------------------------------
The first string of each line is the parameter name, the following string(s) (separated by spaces) is (are) the parameter values.
The parameters can be listed in any order with one parameter per line. 
Comments are started with a '#' - sign. Some of these parameters can be overruled by the command line
parameters given to the :literal:`submit.py` script. 
All parameters have default values; only those parameters which deviate from default
have be listed in the :literal:`CONTROL` files. 


Example CONTROL files
--------------------------------

A number of example files can be found in the directory :literal:`flex_extract_vX.X/Run/Control/`.
They can be used as a template for adaptation, and to understand what can be 
retrievee from ECMWF's archives.
There is an example for each main data set, and in addition, some more varied with respect to resolution, type of field, or way of retrieving the vertical wind. 


 
 
CONTROL file
------------
The file :literal:`CONTROL.documentation` documents the available parameters
in grouped sections together with their default values. 
In :doc:`control_params`, you can find a more
detailed description with additional hints, possible values, and further information about
the setting of these parameters.

.. literalinclude:: ../../../../../Run/Control/CONTROL.documentation 
   :language: bash
   :caption: CONTROL.documentation
    



    
.. toctree::
    :hidden:
    :maxdepth: 2
    
